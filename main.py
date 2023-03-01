# support made on 2023-02-25

from typing import Union, Optional
from base64 import b64encode
from json import loads, dumps
from threading import Thread
from random import randint
from hashlib import sha1
from uuid import uuid4, UUID
from binascii import hexlify
from hmac import new
from time import time, sleep
import os

try:
    from json_minify import json_minify
    from requests import Session, ConnectionError
    from flask import Flask
except ModuleNotFoundError:
    os.system("pip install -r requirements.txt")
    from json_minify import json_minify
    from requests import Session, ConnectionError
    from flask import Flask

import box

Parametros = {
    "comunidad":
        "https://aminoapps.com/c/allcoppel/",

    "monedero": "https://aminoapps.com/c/allcoppel/page/blog/template-default-blog1-title-locale-es/ro3J_JWFeur2PRL7aPvwGbblE3eMlw3wY7fZ", # blog, wiki

    "proxy": None
}

###################
archivo = "acc.json"
###################

def GRIS(*args, tipo: int = 1) -> str:
    return f"\033[{tipo};30m" + " ".join(str(obj) for obj in args) + "\033[0m"


def ROJO(*args, tipo: int = 1) -> str:
    return f"\033[{tipo};31m" + " ".join(str(obj) for obj in args) + "\033[0m"


def VERDE(*args, tipo: int = 1) -> str:
    return f"\033[{tipo};32m" + " ".join(str(obj) for obj in args) + "\033[0m"


def AMARILLO(*args, tipo: int = 1) -> str:
    return f"\033[{tipo};33m" + " ".join(str(obj) for obj in args) + "\033[0m"


def AZUL(*args, tipo: int = 1) -> str:
    return f"\033[{tipo};34m" + " ".join(str(obj) for obj in args) + "\033[0m"


def ROSA(*args, tipo: int = 1) -> str:
    return f"\033[{tipo};35m" + " ".join(str(obj) for obj in args) + "\033[0m"


def CELESTE(*args, tipo: int = 1) -> str:
    return f"\033[{tipo};36m" + " ".join(str(obj) for obj in args) + "\033[0m"


# -----------------------FLASK------------------------
app = Flask(__name__)

@app.route('/')
def home():
    return "~~8;> ~~8;>"
# ----------------------------------------------------

class IPBan(Exception):
    ...

PREFIX = '19'
DEVKEY = 'e7309ecc0953c6fa60005b2765f99dbbc965c8e9'
SIGKEY = 'dfa5ed192dda6e88a12fe12130dc6206b1251e44'

class Amino:

    def __init__(self,
                 dispositivo: str = None,
                 proxy: str = None,
                 uuid: str = None,
                 timeout: int = None) -> None:
        self.proxy=proxy
        self.dispositivo = self.actualizar_dispositivo(dispositivo) \
            if dispositivo else None
        self.sesion = Session()
        self.uuid = uuid or str(uuid4())
        self.timeout = timeout
        self.uid, self.sid = None, None
        self.autenticado = False


    def actualizar_dispositivo(self, dispositivo: str) -> str:
        id = bytes.fromhex(dispositivo)[1:21]
        return self.nuevo_dispositivo(id)


    @staticmethod
    def nuevo_dispositivo(id: bytes = os.urandom(20)) -> str:
        info = bytes.fromhex(PREFIX) + id
        dispositivo = (info + new(
            bytes.fromhex(DEVKEY),
            info, sha1
        ).digest()).hex().upper()
        return dispositivo


    @staticmethod
    def proxyGen():
        proxyList = []
        def check(proxy: str) -> None:
            try:
                ip = session.get("http://api.ipify.org?format=json", proxies=dict(http=proxy), timeout=5).json()["ip"]
                if proxy.startswith(ip):
                    proxyList.append(proxy)
            except Exception:
                pass
        while True:
            with Session() as session:
                proxies = session.get("https://api.proxyscrape.com?proxytype=http&anonymity=elite&country=all&get=true&post=true&request=displayproxies").text.split()
            threads = [Thread(target=check, args=[p]) for p in proxies]
            [{th.setDaemon(True), th.start()} for th in threads]
            while not proxyList:
                sleep(0.3)
            yield proxyList[0]
            proxyList.clear()


    def headers(self, datos: str = None) -> dict:
        if not self.dispositivo:
            self.dispositivo = self.nuevo_dispositivo()
        headers = {
            "NDCDEVICEID": self.dispositivo,
            "SMDEVICEID": str(self.uuid),
            "Accept-Language": "es",
            "Content-Type":
                "application/x-www-form-urlencoded; charset=utf-8",
            "User-Agent":
                #'Dalvik/2.1.0 (Linux; U; Android 7.1; LG-UK495 Build/MRA58K; com.narvii.amino.master/3.3.33180)',
                'Apple iPhone12,1 iOS v15.5 Main/3.12.2',
            "Host": "service.narvii.com",
            "Accept-Encoding": "gzip",
            "Connection": "keep-alive"
        }
        if datos is not None:
            headers["Content-Length"] = str(len(datos))
            headers["NDC-MSG-SIG"] = self.sig(datos)
        if self.sid is not None:
            headers["NDCAUTH"] = "sid=%s" % self.sid
        return headers

    @staticmethod
    def sig(datos: str) -> str:
        signature: str = b64encode(
            bytes.fromhex(PREFIX) + new(
                bytes.fromhex(SIGKEY),
                datos.encode("utf-8"),
                sha1
            ).digest()
        ).decode("utf-8")
        return signature

    def solicitud(self,
                  metodo: str,
                  url: str,
                  datos: dict = None,
                  minify: bool = False) -> dict:
        assert metodo.upper() in ("DELETE", "GET", "POST", "PUT"), "metodo invalido -> %r" % metodo
        url = f"http://service.narvii.com/api/v1/{url}"
        if self.sid is not None:
            url += f"?sid={self.sid}"
        if isinstance(datos, dict):
            datos["timestamp"] = int(time() * 1000)
            datos = dumps(datos)
            if minify is True:
                datos = json_minify(datos)
        with self.sesion.request(
                method=metodo.upper(),
                url=url,
                headers=self.headers(datos),
                data=datos,
                proxies=dict(http=self.proxy),
                timeout=self.timeout
        ) as respuesta:
            try:
                return respuesta.json()
            except Exception:
                raise IPBan(respuesta.text)

    def obtener_desde_link(self, link: str) -> dict:
        return self.solicitud(
            metodo="GET",
            url=f"g/s/link-resolution?q={link}"
        )

    def iniciar_sesion(self,
                       correo: str,
                       contraseña: str) -> dict:
        datos: dict = {
            "email": correo,
            "v": 2,
            "secret": f"0 {contraseña}",
            "deviceID": self.dispositivo,
            "clientType": 100,
            "action": "normal",
        }
        respuesta = self.solicitud(
            metodo="POST",
            url="g/s/auth/login",
            datos=datos
        )
        self.sid = respuesta.get("sid")
        self.uid = respuesta.get("account", {}).get("uid")
        if respuesta["api:statuscode"] == 0:
            self.autenticado = True
        return respuesta

    def entrar_comunidad(self,
                         ndcId: int,
                         invitacionId: Optional[str] = None) -> dict:
        datos = {}
        if invitacionId:
            datos["invitationId"] = invitacionId
        return self.solicitud(
            metodo="POST",
            url=f"x{ndcId}/s/community/join",
            datos=datos
        )

    def loteria(self, ndcId: int, tz: Union[int, str]) -> dict:
        datos = dict(timezone=tz)
        return self.solicitud(
            metodo="POST",
            url=f"x{ndcId}/s/check-in/lottery",
            datos=datos
        )

    def enviar_actividad(self,
                         ndcId: int,
                         tz: int,
                         timers: list) -> dict:
        datos = {
            "userActiveTimeChunkList": timers,
            "optInAdsFlags": 2147483647,
            "timezone": tz
        }
        return self.solicitud(
            metodo="POST",
            url=f"x{ndcId}/s/community/stats/user-active-time",
            datos=datos,
            minify=True
        )

    def obtener_monedero(self) -> dict:
        return self.solicitud(
            metodo="GET",
            url="g/s/wallet",
        )

    def dar_bonos(self,
                         cantidad: int,
                         ndcId: int,
                         blogId: str = None,
                         chatId: str = None,
                         wikiId: str = None) -> dict:
        datos: dict = {
            "coins": cantidad,
            "tippingContext": {
                "transactionId": str(UUID(hexlify(os.urandom(16)).decode('ascii')))
            }
        }
        if blogId:
            url="blog/%s/tipping" % blogId
        elif chatId:
            url="chat/thread/%s/tipping" % chatId
        elif wikiId:
            url=f"tipping"
            datos["objectId"] = wikiId
            datos["objectType"] = 2
        else:
            raise Exception("id no especificado")
        return self.solicitud(
            metodo="POST",
            url=f"x{ndcId}/s/{url}",
            datos=datos
        )

    def subscribirse(self,
                         ndcId: int,
                         uid: str,
                         autoRenovar: bool = False) -> dict:
        datos: dict = {
            "paymentContext": {
                "transactionId": str(UUID(hexlify(os.urandom(16)).decode('ascii'))),
                "isAutoRenew": autoRenovar
            }
        }
        return self.solicitud(
            metodo="POST",
            url="x{ndcId}/s/influencer/{uid}/subscribe",
            datos=datos
        )


class Generador():
    enComunidad = False
    enSesion = 0

    sesionColdown = 1
    comunidadColdown = 1
    loteriaColdown = 7
    actividadColdown = 7

    ndcId = None
    invitacion = None
    proxy = None
    proxyGen = Amino.proxyGen()

    def __init__(self) -> None:
        self.proxy = Parametros.get("proxy")
        amino = Amino(proxy=self.proxy)
        while True:
            try:
                linkInfo = amino.obtener_desde_link(
                    link=Parametros["comunidad"]
                )
                if linkInfo.get("api:statuscode") != 0:
                    print("Comunidad:", linkInfo['api:message'])
                    exit()
                extensions = linkInfo.get("linkInfoV2", {}).get("extensions", {})
                self.ndcId = extensions["community"].get("ndcId", None)
                self.invitacion = extensions.get("invitationId", None)
                linkInfo = amino.obtener_desde_link(
                    link = Parametros["monedero"]
                )["linkInfoV2"]["extensions"]["linkInfo"]
                self.monedero = dict(
                    id = linkInfo["objectId"],
                    tipo = linkInfo["objectType"]
                )
                print(AZUL("- good proxy:"), self.proxy)
                break
            except IPBan:
                print(ROJO("- bad proxy:"), self.proxy if self.proxy else "localhost")
                self.proxy = next(self.proxyGen)

    def enviar_monedas(self,
                         amino: Amino,
                         correo: str) -> None:
        monedero = amino.obtener_monedero()
        monedas = int(monedero.get("wallet", {}).get("totalCoins", 0))
        if self.monedero["tipo"] == 0:
            if monedas < 500:# poner en 500 la taza de subscripcion
                return
            return amino.subscribirse(
                ndcId=self.ndcId,
                uid=self.monedero["id"]
            )
        if monedas < 500:
            return
        if self.monedero["tipo"] == 1:
            destino=dict(blogId=self.monedero["id"])
        elif self.monedero["tipo"] == 2:
            destino=dict(wikiId=self.monedero["id"])
        elif self.monedero["tipo"] == 12:
            destino=dict(chatId=self.monedero["id"])
        for c in range(monedas//500):
            amino.dar_bonos(
                cantidad=500,
                ndcId=self.ndcId,
                **destino
            ); sleep(1)

    def iniciar_sesiones(self,
                         amino: Amino,
                         correo: str,
                         contraseña: str) -> None:
        if amino.autenticado:
            return
        sleep(self.sesionColdown)
        for _ in range(2):
            try:
                resp = amino.iniciar_sesion(
                    correo=correo,
                    contraseña=contraseña
                )
            except ConnectionError as exc:
                if _ == 0:
                    raise ConnectionError(*exc.args) from exc
                continue
            break
        print("[" + AZUL("inicio-de-sesion") + f"][{correo}]: {resp['api:message']}.")

    def entrar_comunidades(self,
                           amino: Amino,
                           correo: str) -> None:
        sleep(self.comunidadColdown)
        for _ in range(2):
            try:
                resp = amino.entrar_comunidad(
                    ndcId=self.ndcId,
                    invitacionId=self.invitacion
                )
            except ConnectionError as exc:
                if _ == 0:
                    raise ConnectionError(*exc.args) from exc
                continue
            break
        print("[" + CELESTE("entrada-en-la-comunidad") + f"][{correo}]: {resp['api:message']}.")

    def loterias(self,
                 amino: Amino,
                 correo: str) -> None:
        sleep(self.loteriaColdown)
        for _ in range(2):
            try:
                resp = amino.loteria(
                    ndcId=self.ndcId,
                    tz=box.tzFilter(hour=23)
                )
            except ConnectionError as exc:
                if _ == 0:
                    raise ConnectionError(*exc.args) from exc
                continue
            break
        print("[" + VERDE("loteria") + f"][{correo}]: {resp['api:message']}")

    def enviar_actividades(self,
                           amino: Amino,
                           correo: str) -> None:
        sleep(self.actividadColdown)
        resp = amino.enviar_actividad(
            ndcId=self.ndcId,
            tz=box.tzFilter(hour=23),
            timers=list(dict(
                start = int(time()),
                end = int(time() + 300)
            ) for _ in range(50))
        )
        print("[" + ROSA("envio-de-actividad") + f"][{correo}]: {resp['api:message']}.")

    def iniciar(self) -> None:
        sleep(3)
        print()
        with open(archivo, "r") as File:
            cuentas = loads(File.read())
        apps = [
            Amino(
                dispositivo=x["device"],
                uuid=x.get("uuid", None),
                proxy=self.proxy
            ) for x in cuentas
        ]
        while True:
            try:
                # tarea; inicio de sesiones
                if (time() - self.enSesion) >= 60 * 60 * 23:
                    [self.iniciar_sesiones(
                        amino=amino,
                        correo=x["email"],
                        contraseña=x["password"],
                    ) for amino, x in zip(
                        apps, cuentas
                    )]
                    print()

                # tarea; entrar en comunidad
                if self.enComunidad is False:
                    [self.entrar_comunidades(
                        amino=amino,
                        correo=x["email"],
                    ) for amino, x in zip(
                        apps, cuentas
                    )]
                    self.enComunidad = True
                    print()

                # tarea; jugar loteria
                if (time() - self.enSesion) >= 60 * 60 * 23:
                    [self.loterias(
                        amino=amino,
                        correo=x["email"],
                    ) for amino, x in zip(
                        apps, cuentas
                    )]
                    self.enSesion = int(time())
                    print()

                # tarea; enviar monedas
                Thread(target=(lambda: [self.enviar_monedas(
                    amino=amino,
                    correo=x["email"]
                ) for amino, x in zip(
                    apps, cuentas
                )])).start()

                # 24 tareas; enviar actividad
                for _ in range(24):
                    [self.enviar_actividades(
                        amino=amino,
                        correo=x["email"],
                    ) for amino, x in zip(
                        apps, cuentas
                    )]
                    print()
                    sleep(3)
                print()

            except IPBan:
                print(ROJO("- bad proxy:"), self.proxy)
                self.proxy = next(self.proxyGen)
                for amino in apps:
                    amino.proxy = self.proxy

            except Exception as Error:
                print(f"[" + ROJO(["correo"]) + "]][" + ROJO("error") + f"]]: {str([Error]).strip('[]')}")


def main() -> None:
    if not Parametros.get("comunidad", "")[::-1][Parametros.get("comunidad", "/")[::-1].index("/")][::-1]:
        print("Link de comunidad no detectada en  %r" % 'Parametros["comunidad"]')
        exit()

    Thread(
        target=app.run,
        kwargs=dict(
            host="0.0.0.0",
            port=randint(2000, 9000)
        )
    ).start()

    generador = Generador()
    generador.iniciar()


if __name__ == "__main__":
    box.clear()
    main()
