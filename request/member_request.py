from marshmallow import Schema, fields, validate, ValidationError
from datetime import date
from flask import jsonify


class MemberSchema(Schema):
    first_name = fields.String(
        required=True,
        validate=validate.Length(min=1, max=20, error="First name must be between 1 and 20 characters.")
    )
    last_name = fields.String(
        required=True,
        validate=validate.Length(min=1, max=20, error="Last name must be between 1 and 20 characters.")
    )
    alias = fields.String(allow_none=True)

    date_of_birth = fields.Date(
        required=True,
        validate=validate.Range(min=date(1900, 1, 1), max=date(2005, 12, 31))
    )

    sex = fields.String(
        required=True,
        validate=validate.OneOf(["male", "female"], error="Sex must be either 'male' or 'female'.")
    )

    threat_level = fields.Integer(
        required=True,
        validate=validate.Range(min=1, max=10)
    )

    gang_id = fields.Integer(allow_none=True)
    country_id = fields.Integer(allow_none=True)