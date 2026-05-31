import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def admin_token(client):
    """Create an admin user and return its token."""
    from app.models.user import User
    from app.security.hash import create_password_hash
    from app.security.jwt import create_access_token
    from tests.conftest import TestingSessionLocal

    session = TestingSessionLocal()
    admin = User(
        username="admin_test",
        email="admin@test.com",
        password=create_password_hash("AdminPass1"),
        role="admin",
    )
    session.add(admin)
    session.commit()
    session.refresh(admin)
    session.close()

    token = create_access_token(data={"sub": "admin_test"})
    return token


@pytest.fixture
def org_token(client):
    from app.models.user import User
    from app.security.hash import create_password_hash
    from app.security.jwt import create_access_token
    from tests.conftest import TestingSessionLocal

    session = TestingSessionLocal()
    org = User(
        username="org_test",
        email="org@test.com",
        password=create_password_hash("OrgPass1"),
        role="organization",
    )
    session.add(org)
    session.commit()
    session.refresh(org)
    session.close()

    token = create_access_token(data={"sub": "org_test"})
    return token


@pytest.fixture
def user_token(client):
    from app.models.user import User
    from app.security.hash import create_password_hash
    from app.security.jwt import create_access_token
    from tests.conftest import TestingSessionLocal

    session = TestingSessionLocal()
    user = User(
        username="user_test",
        email="user@test.com",
        password=create_password_hash("UserPass1"),
        role="user",
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    session.close()

    token = create_access_token(data={"sub": "user_test"})
    return token
