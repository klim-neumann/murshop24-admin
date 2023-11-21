from __future__ import annotations

import datetime
from urllib import parse as urllib_parse

import flask
import murshop24_models as models  # type: ignore
import pytz  # type: ignore
from flask_admin import form as flask_admin_form  # type: ignore
from flask_admin.contrib import sqla as flask_admin_sqla  # type: ignore
from flask_admin.model import typefmt  # type: ignore
from jinja2 import runtime as jinja2_runtime

from murshop24_admin import _telegram

_TG_BOT_WEBHOOK_PATH = "/webhook/{bot_token}"
_PYTZ_TIMEZONE = "Asia/Almaty"


class TgOperatorView(flask_admin_sqla.ModelView):
    column_labels = {"tg_username": "Username"}
    column_list = ("tg_username",)
    form_columns = ("tg_username",)


class TgReviewsChannelView(flask_admin_sqla.ModelView):
    column_list = ("invite_link",)
    form_columns = ("invite_link",)


class TgBotView(flask_admin_sqla.ModelView):
    column_labels = {
        "tg_username": "Username",
        "tg_operator": "Operator",
        "tg_reviews_channel": "Reviews Channel",
    }
    column_list = ("tg_username", "is_running", "tg_operator", "tg_reviews_channel")
    form_columns = ("token", "tg_operator", "tg_reviews_channel")

    def on_model_change(
        self, form: flask_admin_form.BaseForm, model: models.TgBot, is_created: bool
    ):
        del form
        app: flask.Flask = self.admin.app
        tg_bot_host: str = app.config["TG_BOT_HOST"]
        tg_bot_secret_token: str = app.config["TG_BOT_SECRET_TOKEN"]
        get_me_res = _telegram.get_me(model.token)
        if not get_me_res["ok"]:
            raise Exception("Invalid token.")
        tg_id: int = get_me_res["result"]["id"]
        if not is_created and model.tg_id != tg_id:
            raise Exception("The new token does not belong to the previous bot.")
        model.tg_id = tg_id
        model.tg_username = get_me_res["result"]["username"]
        webhook_url = urllib_parse.urljoin(
            tg_bot_host, _TG_BOT_WEBHOOK_PATH.format(bot_token=model.token)
        )
        set_webhook_res = _telegram.set_webhook(
            model.token, webhook_url, tg_bot_secret_token
        )
        if not set_webhook_res["ok"]:
            raise Exception("Webhook setting error.")
        model.is_running = True

    def on_model_delete(self, model: models.TgBot):
        _telegram.delete_webhook(model.token)


class TgCustomerView(flask_admin_sqla.ModelView):
    @staticmethod
    def created_at_column_formatter(
        view: CityView,
        context: jinja2_runtime.Context,
        model: models.TgCustomer,
        name: str,
    ) -> datetime.datetime:
        del view, context, name
        return model.created_at.replace(tzinfo=pytz.utc).astimezone(
            pytz.timezone(_PYTZ_TIMEZONE)
        )

    @staticmethod
    def datetime_type_formatter(
        view: TgCustomerView, value: datetime.datetime, name: str
    ) -> str:
        del view, name
        return value.strftime("%d/%m/%Y %H:%M")

    can_create = False
    can_edit = False
    can_delete = True
    column_labels = {
        "tg_first_name": "First Name",
        "tg_last_name": "Last Name",
        "tg_username": "Username",
    }
    column_list = ("tg_first_name", "tg_last_name", "tg_username", "created_at")
    column_formatters = {"created_at": created_at_column_formatter}
    column_type_formatters = {
        **typefmt.BASE_FORMATTERS,
        datetime.datetime: datetime_type_formatter,
    }


class CityView(flask_admin_sqla.ModelView):
    @staticmethod
    def districts_column_formatter(
        view: CityView, context: jinja2_runtime.Context, model: models.City, name: str
    ) -> list[str]:
        del view, context, name
        return [i.name for i in model.districts]

    column_list = ("name", "districts")
    form_columns = ("name",)
    inline_models = ((models.District, {"form_columns": ("id", "name")}),)
    column_formatters = {"districts": districts_column_formatter}


class ProductView(flask_admin_sqla.ModelView):
    @staticmethod
    def product_units_column_formatter(
        view: CityView,
        context: jinja2_runtime.Context,
        model: models.Product,
        name: str,
    ) -> list[str]:
        del view, context, name
        return [models.ProductUnit.create_str(i) for i in model.product_units]

    column_labels = {"product_units": "Units"}
    column_list = ("name", "description", "product_units")
    form_columns = ("name", "description")
    inline_models = (
        (models.ProductUnit, {"form_columns": ("id", "count", "count_type")}),
    )
    column_formatters = {"product_units": product_units_column_formatter}


class DistrictProductUnitView(flask_admin_sqla.ModelView):
    column_list = ("district", "product_unit", "price")
    form_columns = ("district", "product_unit", "price")


class BankView(flask_admin_sqla.ModelView):
    column_list = ("name",)
    form_columns = ("name",)


class BankAccountView(flask_admin_sqla.ModelView):
    column_list = ("card_number", "phone_number", "bank")
    form_columns = ("card_number", "phone_number", "bank")


class QiwiWalletAccountView(flask_admin_sqla.ModelView):
    column_list = ("phone_number", "nickname")
    form_columns = ("phone_number", "nickname")


class OrderView(flask_admin_sqla.ModelView):
    @staticmethod
    def created_at_column_formatter(
        view: CityView,
        context: jinja2_runtime.Context,
        model: models.TgCustomer,
        name: str,
    ) -> datetime.datetime:
        del view, context, name
        return model.created_at.replace(tzinfo=pytz.utc).astimezone(
            pytz.timezone(_PYTZ_TIMEZONE)
        )

    @staticmethod
    def datetime_type_formatter(
        view: TgCustomerView, value: datetime.datetime, name: str
    ) -> str:
        del view, name
        return value.strftime("%d/%m/%Y %H:%M")

    can_create = False
    can_delete = False
    column_labels = {"tg_customer": "Customer"}
    column_list = (
        "id",
        "price",
        "status",
        "created_at",
        "tg_customer",
        "district",
        "product_unit",
        "bank_account",
        "qiwi_wallet_account",
    )
    form_columns = ("status",)
    column_formatters = {"created_at": created_at_column_formatter}
    column_type_formatters = {
        **typefmt.BASE_FORMATTERS,
        datetime.datetime: datetime_type_formatter,
    }
