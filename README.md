# Serbian Automatic License Plate Reader

Projekat je tek u fazi alfa testiranja, i nije namenjen za ozbiljnu upotrebu.

Iako se ovaj projekat moze upotrebiti za bilo koju regiju, ukljucena su podesavanja za srpsko podrucje. Tu se nalazi fajl koji je treniran na 40.000 srpskih tablica.

## Zahtevi

- OpenCV (3+)
- openALPR
- nodeJS (frontend, nije obavezno)
- Python 2.7 (scipy, numpy, imutils...)
- Linux (Testirano na Ubuntu i CentOS) (Moguce je izmeniti kod kako bi funkcionisao i na windowsu)

## Uputstvo

Za rad je potreban .carinaConfig.ini fajl koji sadrzi podesavanja baze podataka, lokaciju cuvanja slika i same informacije o kamerama. Uz projekat je ukljucen fajl sa osnovnim podesavanjima, promeniti ga po svojim potrebama.

## Mogucnosti konfiguracije

#### kamera
Sekcija: [Kamera1]... (Potrebno je da sekcija pocinje kljucnim parametrom kamera i da bude jedinstveno, npr Kamera1,Kamera2...)
- name: Ime kamere, nije obavezno,dodeljuje se genericko ukoliko nije navedeno
- ip: IP adresa kamere (npr. 178.23.21.48, 192.168.1.10)
- protocol: Protokol koji se koristi za konekciju (rtsp,http)
- username: Korisnicko ime kamere (Nije obavezno, zavisi od podesavanja kamere)
- passwd: Lozinka kamere (Nije obavezno, zavisi od podesavanja kamere)
- vendor: Proizvodjac kamere, potreban je zbog drajvera za konekciju, tj. generisanje linka. Moguce napraviti svoj u carinaLibs/Helper.py
- resolution: Rezolucija kamere (Nije obavezno)
- rotation: Rotacija slike ukoliko je kamera nakrivljena (Nije obavezno)
- roi: Regija od interesa, potrebna je da se ne bi pratilo kretanje na celoj slici (Nije obavezno)
- detectregion: Regija detekcije, potrebna kako bi openalpr brze pronasao tablicu, isecena slika=manja slika=brza detekcija (Nije obavezno)
- fps: Frejmovi po sekundi (Nije obavezno)
- sensitivity: Osetljivost pokreta (Nije obavezno)

#### Baza podataka
Sekcija: [database]
Klasicno, username,host,password i naziv baze

#### Lokacija cuvanja
Sekcija: [storage]
- image: lokacija na kojoj se cuvaju slike (pozeljno je da bude apsolutna)
- thumbnails: Lokacija thumbnaila

## Frontend

Ukljucena je i ta funkcionalnost, potrebno je izmeniti frontend/views/index.jade po svom ukusu (ili bar IP adresu kamere i lokaciju slika)

Server se startuje ulaskom u frontend folder i komandom __node bin/www__ ili __nohup node bin/www &__ i zatim posetiti __http://localhost:3000__
