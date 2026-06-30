import asyncio
import unittest

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth.dependencies import get_current_user_ws
from app.auth.security import create_access_token
from app.models.operator import Operator


class WebSocketAuthTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Operator.__table__.create(self.engine)
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
        )
        self.db = self.SessionLocal()
        self.db.add(
            Operator(
                username="admin",
                password_hash="not-used-by-token-validation",
                role="admin",
            )
        )
        self.db.commit()

    def tearDown(self):
        self.db.close()
        Operator.__table__.drop(self.engine)
        self.engine.dispose()

    def test_websocket_auth_accepts_valid_token_with_explicit_db_session(self):
        token = create_access_token({"sub": "admin", "role": "admin"})

        user = asyncio.run(get_current_user_ws(token, self.db))

        self.assertEqual(user.username, "admin")
        self.assertEqual(user.role, "admin")

    def test_websocket_auth_rejects_invalid_token(self):
        with self.assertRaises(HTTPException):
            asyncio.run(get_current_user_ws("invalid-token", self.db))

    def test_websocket_auth_rejects_unknown_user(self):
        token = create_access_token({"sub": "missing-user", "role": "admin"})

        with self.assertRaises(HTTPException):
            asyncio.run(get_current_user_ws(token, self.db))


if __name__ == "__main__":
    unittest.main()
