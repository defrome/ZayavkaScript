from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from models import Application, ApplicationSource, ApplicationStatus, Master, MasterTime, Service, User


ACTIVE_STATUSES = (ApplicationStatus.NEW, ApplicationStatus.IN_PROGRESS)


class ApplicationService:
    def __init__(self, db: Session):
        self.db = db

    def _serialize(self, application: Application) -> dict:
        return {
            "id": application.id,
            "service_id": application.service_id,
            "service_name": application.service.name,
            "user_id": application.user_id,
            "customer_name": application.user.name,
            "customer_phone": application.user.telephone_number,
            "master_id": application.master_id,
            "master_name": application.master.name if application.master else None,
            "appointment_date": application.appointment_date,
            "time_slot": application.time_slot,
            "status": application.status,
            "source": application.source,
            "comment": application.comment,
            "created_at": application.created_at,
        }

    def _get_service(self, service_id: int) -> Service:
        service = self.db.query(Service).filter(Service.id == service_id, Service.is_active.is_(True)).first()
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Услуга с ID {service_id} не найдена",
            )
        return service

    def _get_or_create_user(self, name: str, telephone_number: str) -> User:
        normalized_phone = telephone_number.strip()
        user = self.db.query(User).filter(User.telephone_number == normalized_phone).first()
        if user:
            user.name = name.strip()
            return user

        user = User(name=name.strip(), telephone_number=normalized_phone)
        self.db.add(user)
        self.db.flush()
        return user

    def _reserve_master_slot(self, master_id: int, appointment_date: date, time_slot: str) -> tuple[Master, MasterTime]:
        master = self.db.query(Master).filter(Master.id == master_id, Master.is_active.is_(True)).first()
        if not master:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Мастер с id {master_id} не найден",
            )

        slot = (
            self.db.query(MasterTime)
            .filter(
                MasterTime.master_id == master.id,
                MasterTime.day == appointment_date,
                MasterTime.time_slot == time_slot,
            )
            .with_for_update()
            .first()
        )

        if slot is None:
            slot = MasterTime(master_id=master.id, day=appointment_date, time_slot=time_slot, is_available=True)
            self.db.add(slot)
            self.db.flush()

        if not slot.is_available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Этот слот уже занят",
            )

        active_conflict = (
            self.db.query(Application)
            .filter(
                Application.master_id == master.id,
                Application.appointment_date == appointment_date,
                Application.time_slot == time_slot,
                Application.status.in_(ACTIVE_STATUSES),
            )
            .first()
        )
        if active_conflict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="На это время уже есть активная заявка",
            )

        slot.is_available = False
        return master, slot

    def create_public_application(
        self,
        service_id: int,
        master_id: int | None,
        name: str,
        telephone_number: str,
        appointment_date: date,
        time_slot: str,
        comment: str | None,
    ) -> dict:
        try:
            service = self._get_service(service_id)
            user = self._get_or_create_user(name=name, telephone_number=telephone_number)

            reserved_master_id = None
            reserved_slot_id = None
            if master_id is not None:
                master, slot = self._reserve_master_slot(master_id, appointment_date, time_slot)
                reserved_master_id = master.id
                reserved_slot_id = slot.id

            application = Application(
                service_id=service.id,
                user_id=user.id,
                master_id=reserved_master_id,
                master_time_id=reserved_slot_id,
                appointment_date=appointment_date,
                time_slot=time_slot,
                status=ApplicationStatus.NEW,
                source=ApplicationSource.USER,
                comment=comment,
            )
            self.db.add(application)
            self.db.commit()
            self.db.refresh(application)
            application_id = application.id
        except HTTPException:
            self.db.rollback()
            raise
        except Exception as exc:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при создании заявки: {exc}",
            ) from exc

        loaded = self._load_application(application_id)
        return self._serialize(loaded)

    def create_admin_application(
        self,
        service_id: int,
        name: str,
        telephone_number: str,
        appointment_date: date,
        time_slot: str,
        master_id: int,
        comment: str | None,
    ) -> dict:
        try:
            service = self._get_service(service_id)
            user = self._get_or_create_user(name=name, telephone_number=telephone_number)
            master, slot = self._reserve_master_slot(master_id, appointment_date, time_slot)

            application = Application(
                service_id=service.id,
                user_id=user.id,
                master_id=master.id,
                master_time_id=slot.id,
                appointment_date=appointment_date,
                time_slot=time_slot,
                status=ApplicationStatus.IN_PROGRESS,
                source=ApplicationSource.ADMIN,
                comment=comment,
            )
            self.db.add(application)
            self.db.commit()
            self.db.refresh(application)
            application_id = application.id
        except HTTPException:
            self.db.rollback()
            raise
        except Exception as exc:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при создании админ-заявки: {exc}",
            ) from exc

        loaded = self._load_application(application_id)
        return self._serialize(loaded)

    def _load_application(self, application_id: int) -> Application:
        application = (
            self.db.query(Application)
            .options(
                joinedload(Application.service),
                joinedload(Application.user),
                joinedload(Application.master),
            )
            .filter(Application.id == application_id)
            .first()
        )
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Заявка {application_id} не найдена",
            )
        return application

    def list_applications(
        self,
        only_active: bool = False,
        status_filter: ApplicationStatus | None = None,
    ) -> list[dict]:
        query = self.db.query(Application).options(
            joinedload(Application.service),
            joinedload(Application.user),
            joinedload(Application.master),
        )

        if only_active:
            query = query.filter(Application.status.in_(ACTIVE_STATUSES))

        if status_filter:
            query = query.filter(Application.status == status_filter)

        apps = query.order_by(Application.created_at.desc()).all()
        return [self._serialize(app) for app in apps]

    def update_status(self, application_id: int, new_status: ApplicationStatus) -> dict:
        try:
            application = (
                self.db.query(Application)
                .options(joinedload(Application.master_time))
                .filter(Application.id == application_id)
                .with_for_update()
                .first()
            )

            if not application:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Заявка {application_id} не найдена",
                )

            application.status = new_status

            if application.master_time is not None:
                if new_status in (ApplicationStatus.COMPLETED, ApplicationStatus.CANCELED):
                    application.master_time.is_available = True
                elif new_status in ACTIVE_STATUSES:
                    application.master_time.is_available = False

            self.db.commit()
        except HTTPException:
            self.db.rollback()
            raise
        except Exception as exc:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка изменения статуса: {exc}",
            ) from exc

        app = self._load_application(application_id)
        return self._serialize(app)
