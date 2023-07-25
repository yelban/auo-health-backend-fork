import hmac
import uuid
from datetime import datetime, timedelta
from enum import Enum
from functools import cached_property
from typing import Any, Dict, Optional, Union

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from cryptography.fernet import Fernet
from fastapi import Request, Response
from jose import jwt
from passlib.context import CryptContext

from auo_project.core.config import AuthConfig, settings
from auo_project.core.exceptions import (
    AccessTokenRequired,
    CSRFError,
    FingerprintError,
    FreshTokenRequired,
    InvalidHeaderError,
    JWTDecodeError,
    MissingTokenError,
    RefreshTokenRequired,
    RevokedTokenError,
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
fernet = Fernet(str.encode(settings.ENCRYPT_KEY))


class TokenType(str, Enum):
    access = "access"
    refresh = "refresh"


def decode_jwt_token(encoded_token: str, secret_key: str):
    if not encoded_token:
        return ""
    algorithms = [AuthConfig._algorithm]
    return jwt.decode(
        encoded_token,
        secret_key,
        # issuer=issuer,
        # audience=self._decode_audience,
        # leeway=self._decode_leeway,
        algorithms=algorithms,
    )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def get_data_encrypt(data) -> str:
    data = fernet.encrypt(data.encode())
    return data.decode()


def get_data_decrypt(variable: str) -> str:
    return fernet.decrypt(variable.encode()).decode()


class AuthJWT(AuthConfig):
    def __init__(self, req: Request = None, res: Response = None) -> None:
        """
        Get JWT in the cookie
        :param req: all incoming request
        :param res: response from endpoint
        """
        if res:
            self._response = res

        if req:
            self._request = req

    def _get_jwt_identifier(self) -> str:
        return str(uuid.uuid4())

    def get_jwt_subject(self) -> Optional[Union[str, int]]:
        """
        this will return the subject of the JWT that is accessing this endpoint.
        If no JWT is present, `None` is returned instead.
        :return: sub of JWT
        """
        if self._token:
            return self._verified_token(self._token)["sub"]
        return

    @property
    def jwt_jti(self) -> str:
        return self._jti

    @jwt_jti.setter
    def jwt_jti(self, value):
        self._jti = value

    @property
    def csrf_token(self) -> str:
        return self._csrf_token

    @csrf_token.setter
    def csrf_token(self, value):
        self._csrf_token = value

    def create_token(
        self,
        subject: Union[str, Any],
        type_token: str,
        exp_time: timedelta,
        user_claims: Optional[Dict] = {},
    ) -> str:
        """
        jti
        csrf
        fingerprint: encoded csrf token by fernet
        """
        # TODO: save jti, exp to db
        jwt_jti = self._get_jwt_identifier()
        # TODO: check use the same or not (access and refresh)
        self.csrf_token = self._get_jwt_identifier()

        reserved_claims = {
            "sub": str(subject),
            "iat": datetime.utcnow(),
            "nbf": datetime.utcnow(),
            "exp": exp_time,
            "jti": jwt_jti,
            # "iss":
            # "aud":
        }
        custom_claims = {
            "type": type_token,
            "csrf": self.csrf_token,
            "fingerprint": get_data_encrypt(self.csrf_token),
        }
        encoded_jwt = jwt.encode(
            {**reserved_claims, **custom_claims, **user_claims},
            settings.SECRET_KEY,
            algorithm=self._algorithm,
        )
        return encoded_jwt

    def create_access_token(
        self,
        subject: Union[str, Any],
        expires_delta: timedelta = None,
        user_claims: Optional[Dict] = {},
    ) -> str:
        """
        Create a access token with 15 minutes for expired time (default),
        info for param and return check to function create token
        :return: encoded token
        """
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            )
        return self.create_token(
            subject=subject,
            type_token=TokenType.access.value,
            exp_time=expire,
        )

    def create_refresh_token(
        self,
        subject: Union[str, Any],
        expires_delta: timedelta = None,
        user_claims: Optional[Dict] = {},
    ) -> str:
        """
        Create a refresh token with 30 days for expired time (default),
        info for param and return check to function create token
        :return: encoded token
        """
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES,
            )
        return self.create_token(
            subject=subject,
            type_token=TokenType.refresh.value,
            exp_time=expire,
        )

    def set_access_cookies(
        self,
        encoded_access_token: str,
        response: Optional[Response] = None,
        max_age: Optional[int] = None,
    ) -> None:
        """
        Configures the response to set access token in a cookie.
        this will also set the CSRF double submit values in a separate cookie
        :param encoded_access_token: The encoded access token to set in the cookies
        :param response: The FastAPI response object to set the access cookies in
        :param max_age: The max age of the cookie value should be the number of seconds (integer)
        """
        if max_age and not isinstance(max_age, int):
            raise TypeError("max_age must be a integer")
        if response and not isinstance(response, Response):
            raise TypeError("The response must be an object response FastAPI")

        response = response or self._response

        # Set the access JWT in the cookie
        response.set_cookie(
            self._access_cookie_key,
            encoded_access_token,
            max_age=max_age or self._cookie_max_age,
            path=self._access_cookie_path,
            domain=self._cookie_domain,
            secure=self._cookie_secure,
            httponly=True,
            samesite=self._cookie_samesite,
        )

        # If enabled, set the csrf double submit access cookie
        if self._cookie_csrf_protect:
            response.set_cookie(
                self._access_csrf_cookie_key,
                self.csrf_token,
                max_age=max_age or self._cookie_max_age,
                path=self._access_csrf_cookie_path,
                domain=self._cookie_domain,
                secure=self._cookie_secure,
                httponly=False,
                samesite=self._cookie_samesite,
            )

        # if self._cookie_csrf_protect:
        #     response.set_cookie(
        #         self._access_csrf_cookie_key + "123",
        #         self.csrf_token,
        #         max_age=max_age or self._cookie_max_age,
        #         path=self._access_csrf_cookie_path,
        #         domain="*.deepinsight.tw",
        #         # secure=self._cookie_secure,
        #         httponly=False,
        #         samesite="none",
        #     )

    def set_refresh_cookies(
        self,
        encoded_refresh_token: str,
        response: Optional[Response] = None,
        max_age: Optional[int] = None,
    ) -> None:
        """
        Configures the response to set refresh token in a cookie.
        this will also set the CSRF double submit values in a separate cookie
        :param encoded_refresh_token: The encoded refresh token to set in the cookies
        :param response: The FastAPI response object to set the refresh cookies in
        :param max_age: The max age of the cookie value should be the number of seconds (integer)
        """
        if max_age and not isinstance(max_age, int):
            raise TypeError("max_age must be a integer")
        if response and not isinstance(response, Response):
            raise TypeError("The response must be an object response FastAPI")

        response = response or self._response

        # Set the refresh JWT in the cookie
        response.set_cookie(
            self._refresh_cookie_key,
            encoded_refresh_token,
            max_age=max_age or self._cookie_max_age,
            path=self._refresh_cookie_path,
            domain=self._cookie_domain,
            secure=self._cookie_secure,
            httponly=True,
            samesite=self._cookie_samesite,
        )

        # set the csrf double submit refresh cookie
        response.set_cookie(
            self._refresh_csrf_cookie_key,
            self.csrf_token,
            max_age=max_age or self._cookie_max_age,
            path=self._refresh_csrf_cookie_path,
            domain=self._cookie_domain,
            secure=self._cookie_secure,
            httponly=False,
            samesite=self._cookie_samesite,
        )

    def unset_jwt_cookies(self, response: Optional[Response] = None) -> None:
        """
        Unset (delete) all jwt stored in a cookie
        :param response: The FastAPI response object to delete the JWT cookies in.
        """
        self.unset_access_cookies(response)
        self.unset_refresh_cookies(response)

    def unset_access_cookies(self, response: Optional[Response] = None) -> None:
        """
        Remove access token and access CSRF double submit from the response cookies
        :param response: The FastAPI response object to delete the access cookies in.
        """
        if not self.jwt_in_cookies:
            raise RuntimeWarning(
                "unset_access_cookies() called without 'authjwt_token_location' configured to use cookies",
            )

        if response and not isinstance(response, Response):
            raise TypeError("The response must be an object response FastAPI")

        response = response or self._response

        response.delete_cookie(
            self._access_cookie_key,
            path=self._access_cookie_path,
            domain=self._cookie_domain,
        )

        response.delete_cookie(
            self._access_csrf_cookie_key,
            path=self._access_csrf_cookie_path,
            domain=self._cookie_domain,
        )

    def unset_refresh_cookies(self, response: Optional[Response] = None) -> None:
        """
        Remove refresh token and refresh CSRF double submit from the response cookies
        :param response: The FastAPI response object to delete the refresh cookies in.
        """
        if not self.jwt_in_cookies:
            raise RuntimeWarning(
                "unset_refresh_cookies() called without 'authjwt_token_location' configured to use cookies",
            )

        if response and not isinstance(response, Response):
            raise TypeError("The response must be an object response FastAPI")

        response = response or self._response

        response.delete_cookie(
            self._refresh_cookie_key,
            path=self._refresh_cookie_path,
            domain=self._cookie_domain,
        )

        response.delete_cookie(
            self._refresh_csrf_cookie_key,
            path=self._refresh_csrf_cookie_path,
            domain=self._cookie_domain,
        )

    def _verify_and_get_jwt_in_cookies(
        self,
        type_token: str,
        request: Request,
        csrf_token: Optional[str] = None,
        fresh: Optional[bool] = False,
    ) -> "AuthJWT":
        """
        Check if cookies have a valid access or refresh token. if an token present in
        cookies, self._token will set. raises exception error when an access or refresh token
        is invalid or doesn't match with CSRF token double submit
        :param type_token: indicate token is access or refresh token
        :param request: for identity get cookies from HTTP or WebSocket
        :param csrf_token: the CSRF double submit token
        :param fresh: check freshness token if True
        """
        if type_token not in ["access", "refresh"]:
            raise ValueError("type_token must be between 'access' or 'refresh'")
        if not isinstance(request, Request):
            raise TypeError("request must be an instance of 'Request'")

        if type_token == "access":
            cookie_key = self._access_cookie_key
            cookie = request.cookies.get(cookie_key) or request.headers.get(
                cookie_key.replace("_", "-"),
            )
            csrf_token = request.headers.get(self._access_csrf_header_name)
            # print('access', cookie, csrf_token)
        if type_token == "refresh":
            cookie_key = self._refresh_cookie_key
            cookie = request.cookies.get(cookie_key) or request.headers.get(
                cookie_key.replace("_", "-"),
            )
            csrf_token = request.headers.get(self._refresh_csrf_header_name)

        if not cookie:
            # TODO: fixme
            raise MissingTokenError(
                status_code=401,
                message="Missing cookie {}".format(cookie_key),
            )

        if self._cookie_csrf_protect and not csrf_token:
            if request.method in self._csrf_methods:
                raise CSRFError(status_code=401, message="Missing CSRF Token")

        # set token from cookie and verify jwt
        self._token = cookie
        self._decoded_token = self.get_raw_jwt
        self._verify_jwt_in_request(self._decoded_token, type_token, "cookies", fresh)

        # TODO: handle is_localhost
        is_localhost = False
        if request and request.headers:
            is_localhost = "http://localhost:3000" in request.headers.get("origin", "")
        is_localhost = True
        if self._cookie_csrf_protect and csrf_token and is_localhost is False:
            if request.method in self._csrf_methods:
                if "csrf" not in self._decoded_token:
                    raise JWTDecodeError(status_code=401, message="Missing claim: csrf")
                if not hmac.compare_digest(csrf_token, self._decoded_token["csrf"]):
                    raise CSRFError(
                        status_code=401,
                        message="CSRF double submit tokens do not match",
                    )

    def _has_token_in_denylist_callback(self) -> bool:
        """
        Return True if token denylist callback set
        """
        return self._token_in_denylist_callback is not None

    def _check_token_is_revoked(
        self,
        raw_token: Dict[str, Union[str, int, bool]],
    ) -> None:
        """
        Ensure that AUTHJWT_DENYLIST_ENABLED is true and callback regulated, and then
        call function denylist callback with passing decode JWT, if true
        raise exception Token has been revoked
        """
        if not self._denylist_enabled:
            return

        if not self._has_token_in_denylist_callback():
            raise RuntimeError(
                "A token_in_denylist_callback must be provided via "
                "the '@AuthJWT.token_in_denylist_loader' if "
                "authjwt_denylist_enabled is 'True'",
            )

        if self._token_in_denylist_callback.__func__(raw_token):
            raise RevokedTokenError(status_code=401, message="Token has been revoked")

    def _verifying_token(
        self,
        encoded_token: str,
        issuer: Optional[str] = None,
    ) -> None:
        """
        Verified token and check if token is revoked
        :param encoded_token: token hash
        :param issuer: expected issuer in the JWT
        """
        raw_token = self._verified_token(encoded_token, issuer)
        if raw_token["type"] in self._denylist_token_checks:
            self._check_token_is_revoked(raw_token)

    def _verified_token(
        self,
        encoded_token: str,
        issuer: Optional[str] = None,
    ) -> Dict[str, Union[str, int, bool]]:
        """
        Verified token and catch all error from jwt package and return decode token
        :param encoded_token: token hash
        :param issuer: expected issuer in the JWT
        :return: raw data from the hash token in the form of a dictionary
        """
        algorithms = [self._algorithm]

        try:
            unverified_headers = self.get_unverified_jwt_headers(encoded_token)
        except Exception as err:
            raise InvalidHeaderError(status_code=401, message=str(err))

        try:
            # secret_key = self._secret_key
            secret_key = settings.SECRET_KEY
        except Exception:
            raise

        try:
            return jwt.decode(
                encoded_token,
                secret_key,
                # issuer=issuer,
                # audience=self._decode_audience,
                # leeway=self._decode_leeway,
                algorithms=algorithms,
            )
        except Exception as err:
            raise JWTDecodeError(status_code=401, message=str(err))

    def _verify_jwt_in_request(
        self,
        decoded_token: Dict[str, Union[str, int, bool]],
        type_token: str,
        token_from: str,
        fresh: Optional[bool] = False,
    ) -> None:
        """
        Ensure that the requester has a valid token. this also check the freshness of the access token
        :param decoded_token: The decoded JWT
        :param type_token: indicate token is access or refresh token
        :param token_from: indicate token from headers cookies, websocket
        :param fresh: check freshness token if True
        """
        if type_token not in ["access", "refresh"]:
            raise ValueError("type_token must be between 'access' or 'refresh'")
        if token_from not in ["headers", "cookies"]:
            raise ValueError("token_from must be between 'headers', 'cookies'")

        # verify jwt
        # TODO: fixme
        # issuer = self._decode_issuer if type_token == "access" else None
        # TODO: enable me
        # self._verifying_token(decoded_token, issuer)
        # print('decoded_token', decoded_token)
        if decoded_token["type"] != type_token:
            msg = "Only {} tokens are allowed".format(type_token)
            if type_token == "access":
                raise AccessTokenRequired(status_code=401, message=msg)
            if type_token == "refresh":
                raise RefreshTokenRequired(status_code=401, message=msg)

        if fresh and not decoded_token["fresh"]:
            raise FreshTokenRequired(status_code=401, message="Fresh token required")

    def verify_jwt(
        self,
        type_token: str,
        request: Request,
        csrf_token: Optional[str] = None,
        fresh: Optional[bool] = False,
    ):
        """
        Check if cookies have a valid access or refresh token. if an token present in
        cookies, self._token will set raises exception error when an access or refresh token
        is invalid or doesn't match with CSRF token double submit
        :param type_token: indicate token is access or refresh token
        :param request: for identity get cookies from HTTP or WebSocket
        :param csrf_token: the CSRF double submit token
        :param fresh: check freshness token if True.
                      See also the [link](https://github.com/IndominusByte/fastapi-jwt-auth/blob/a6c06193319da0e4976c7472966f3a2891e0d50c/docs/usage/freshness.md)
                      to get more details.
        """
        if type_token not in ["access", "refresh"]:
            raise ValueError("type_token must be between 'access' or 'refresh'")
        if not isinstance(request, (Request)):
            raise TypeError("request must be an instance of 'Request'")

        if type_token == "access":
            cookie_key = self._access_cookie_key
            cookie = request.cookies.get(cookie_key)
        if type_token == "refresh":
            cookie_key = self._refresh_cookie_key
            cookie = request.cookies.get(cookie_key)
            csrf_token = request.headers.get(self._refresh_csrf_header_name)

        if not cookie:
            raise MissingTokenError(
                status_code=401,
                message="Missing cookie {}".format(cookie_key),
            )

        if not csrf_token:
            raise CSRFError(status_code=401, message="Missing CSRF Token")

        # set token from cookie and verify jwt
        self._token = cookie
        self._decoded_token = self.get_raw_jwt
        self._verify_jwt_in_request(self._decoded_token, type_token, "cookies", fresh)

        # TODO: handle is_localhost
        is_localhost = False
        if request and request.headers:
            is_localhost = "http://localhost:3000" in request.headers.get("origin", "")
        is_localhost = True
        if self._cookie_csrf_protect and csrf_token and not is_localhost:
            if "csrf" not in self._decoded_token:
                raise JWTDecodeError(status_code=401, message="Missing claim: csrf")
            if "fingerprint" not in self._decoded_token:
                raise JWTDecodeError(
                    status_code=401,
                    message="Missing claim: fingerprint",
                )
            if not hmac.compare_digest(csrf_token, self._decoded_token["csrf"]):
                raise CSRFError(
                    status_code=401,
                    message="CSRF double submit tokens do not match",
                )
            if not hmac.compare_digest(
                get_data_encrypt(csrf_token),
                self._decoded_token["fingerprint"],
            ):
                raise FingerprintError(
                    status_code=401,
                    message="The fingerprint token do not match",
                )

    @cached_property
    def get_raw_jwt(self) -> Optional[Dict[str, Union[str, int, bool]]]:
        """
        this will return the python dictionary which has all of the claims of the JWT that is accessing the endpoint.
        If no JWT is currently present, return None instead
        :return: claims of JWT
        """
        token = self._token
        if token:
            return self._verified_token(token)
        return None

    def jwt_access_token_required(
        self,
    ) -> None:
        """
        Only access token can access this function
        """
        self._verify_and_get_jwt_in_cookies("access", self._request)

    def jwt_refresh_token_required(
        self,
    ) -> None:
        """
        This function will ensure that the requester has a valid refresh token
        """
        self._verify_and_get_jwt_in_cookies("refresh", self._request)

    def get_unverified_jwt_headers(self, encoded_token: Optional[str] = None) -> dict:
        """
        Returns the Headers of an encoded JWT without verifying the actual signature of JWT
        :param encoded_token: The encoded JWT to get the Header from
        :return: JWT header parameters as a dictionary
        """
        encoded_token = encoded_token or self._token

        return jwt.get_unverified_header(encoded_token)


def decrypt(key, iv, data):
    # 以金鑰搭配 CBC 模式與初始向量建立 cipher 物件
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)

    # 解密後進行 unpadding
    original_data = unpad(cipher.decrypt(data), AES.block_size, style="pkcs7")

    return original_data


def encrypt(key, iv, data):
    ## new 一個 AES CBC cipher
    cipher = AES.new(key, AES.MODE_CBC, iv)

    ## 將要加密的 data encode 成 utf-8
    ## 然後使用 pad function 將明文 padding 到 block size
    return cipher.encrypt(pad(data, AES.block_size))
