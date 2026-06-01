from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.registration import RegistrationCreate, RegstrationResponse
from app.services.registration_service import RegistrationService
from app.depend.current_user import get_current_user, required_admin
from app.services.event_service import EventOperations
from app.services.EMAIL_SERVICE.notification_service import NotificationService
# from app.utils.logger_ import logger


router = APIRouter()
notification = NotificationService()


@router.post("/create/", response_model=RegstrationResponse, status_code=status.HTTP_201_CREATED)
async def create_registration(
    event_id: int,
    # dbRegistrationCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    event_ops = EventOperations(db)
    event = event_ops.get_event_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    print(f"""
          {current_user.username}

          {event.title}
          """)

    # NotificationService.send_registration_confirmation(
    #     recipient_email=current_user.get("email"),
    #     user_name=current_user.get("username"),
    #     event_name=event.title
    # )


    if current_user.role == "user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only register yourself for events"
        )
    from app.schemas.registration import RegistrationCreate
    registration = RegistrationCreate(
        user_id=current_user.id,
        event_id=event.id
    )

    # registration.user_id = current_user.id
    # registration.event_id = event.id

    notification.send_registration_confirmation(
        recipient_email=current_user.email,
        user_name=current_user.username,
        event_name=event.title
    )


    registration_service = RegistrationService(db)
    return registration_service.create_registration(registration)

@router.get("/get_registrations/", response_model=list[RegstrationResponse])
async def get_registrations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    user_id = current_user.id
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")


    registration_service = RegistrationService(db)
    registrations = registration_service.get_registrations_by_user(user_id)
    if not registrations:
        raise HTTPException(status_code=404, detail="No registrations found for this user")
    return registrations



@router.get("/get_registrations_by_user/{user_id}", response_model=list[RegstrationResponse])
async def get_registrations_by_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view these registrations"
        )

    registration_service = RegistrationService(db)
    registrations = registration_service.get_registrations_by_user(user_id)
    if not registrations:
        raise HTTPException(status_code=404, detail="No registrations found for this user")
    return registrations



@router.get("/get_registrations_by_event/{event_id}", response_model=list[RegstrationResponse])
async def get_registrations_by_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    if current_user.role not in ["admin", "organization"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins or event organizers can view event registrations"
        )

    registration_service = RegistrationService(db)
    registrations = registration_service.get_registrations_by_event(event_id)
    if not registrations:
        raise HTTPException(status_code=404, detail="No registrations found for this event")
    return registrations

@router.get("/get_registration/{registration_id}", response_model=RegstrationResponse)
async def get_registration(
    registration_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    registration_service = RegistrationService(db)
    registration = registration_service.get_registration_by_id(registration_id)

    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")

    # Check authorization
    event_ops = EventOperations(db)
    event = event_ops.get_event_by_id(registration.event_id)

    if (current_user.role == "admin" or
        current_user.id == registration.user_id or
        (current_user.role == "organization" and event and event.organizer_id == current_user.id)):
        return registration

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not authorized to view this registration"
    )


@router.delete("/cancel_registration/{registration_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_registration(
    registration_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    registration_service = RegistrationService(db)
    registration = registration_service.get_registration_by_id(registration_id)

    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")

    event_ops = EventOperations(db)
    event = event_ops.get_event_by_id(registration.event_id)

    if (current_user.role == "admin" or
        current_user.id == registration.user_id or
        (current_user.role == "organization" and event and event.organizer_id == current_user.id)):
        registration_service.cancel_registration(registration_id)
        return None

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not authorized to cancel this registration"
    )