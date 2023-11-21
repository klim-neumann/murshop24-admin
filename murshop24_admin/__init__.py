import enum
import secrets

import flask
import flask_admin  # type: ignore
import flask_sqlalchemy as flask_sqla
import murshop24_models as models  # type: ignore
import sqlalchemy as sqla
from flask_sqlalchemy import session as flask_sqla_session
from sqlalchemy import orm

from murshop24_admin import _settings, _views

_SQLA_ENGINE_DRIVER = "postgresql+psycopg"
_SECRET_KEY_NBYTES = 16
_TEMPLATE_MODE = "bootstrap3"


class ModelViewCategory(enum.StrEnum):
    TELEGRAM = "Telegram"
    PRODUCT = "Product"
    PAYMENT = "Payment"


def _create_admin(
    app: flask.Flask, session: orm.scoped_session[flask_sqla_session.Session]
) -> flask_admin.Admin:
    admin = flask_admin.Admin(app=app, template_mode=_TEMPLATE_MODE)
    admin.add_views(
        _views.CityView(models.City, session),
        _views.OrderView(models.Order, session),
        _views.TgOperatorView(
            models.TgOperator,
            session,
            name="Operator",
            category=ModelViewCategory.TELEGRAM,
        ),
        _views.TgReviewsChannelView(
            models.TgReviewsChannel,
            session,
            name="Reviews Channel",
            category=ModelViewCategory.TELEGRAM,
        ),
        _views.TgBotView(
            models.TgBot, session, name="Bot", category=ModelViewCategory.TELEGRAM
        ),
        _views.TgCustomerView(
            models.TgCustomer,
            session,
            name="Customer",
            category=ModelViewCategory.TELEGRAM,
        ),
        _views.ProductView(models.Product, session, category=ModelViewCategory.PRODUCT),
        _views.DistrictProductUnitView(
            models.DistrictProductUnit,
            session,
            name="Price",
            category=ModelViewCategory.PRODUCT,
        ),
        _views.BankView(models.Bank, session, category=ModelViewCategory.PAYMENT),
        _views.BankAccountView(
            models.BankAccount, session, category=ModelViewCategory.PAYMENT
        ),
        _views.QiwiWalletAccountView(
            models.QiwiWalletAccount, session, category=ModelViewCategory.PAYMENT
        ),
    )
    return admin


def _create_app() -> flask.Flask:
    postgres_settings = _settings.PostgresSettings()  # type: ignore
    tg_bot_settings = _settings.TgBotSettings()  # type: ignore
    app = flask.Flask(__name__)
    sqla_url = sqla.URL.create(
        _SQLA_ENGINE_DRIVER,
        username=postgres_settings.user,
        password=postgres_settings.password,
        host=postgres_settings.host,
        port=postgres_settings.port,
        database=postgres_settings.db,
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = sqla_url.render_as_string(
        hide_password=False
    )
    app.config["SECRET_KEY"] = secrets.token_hex(nbytes=_SECRET_KEY_NBYTES)
    app.config["TG_BOT_HOST"] = tg_bot_settings.host
    app.config["TG_BOT_SECRET_TOKEN"] = tg_bot_settings.secret_token
    db = flask_sqla.SQLAlchemy(app=app, model_class=models.Base)
    with app.app_context():
        db.create_all()
    _create_admin(app, db.session)
    return app


app = _create_app()
