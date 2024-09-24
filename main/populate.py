# encoding:utf-8
from bs4 import BeautifulSoup
import urllib.request
import os
import shutil
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, KEYWORD, STORED, NUMERIC
from django.shortcuts import render, redirect
from main.models import Pelicula, Actor, Genero, Personal

urlGeneral = "https://www.themoviedb.org"
listaURLsPeliculas = [
    "https://www.themoviedb.org/genre/12-aventura/movie?language=es-ES",
    "https://www.themoviedb.org/genre/28-accion/movie?language=es-ES",
    "https://www.themoviedb.org/genre/14-fantasia/movie?language=es-ES",
    "https://www.themoviedb.org/genre/35-comedia/movie?language=es-ES",
    "https://www.themoviedb.org/genre/16-animacion/movie?language=es-ES"
]

def get_peliculas():
    listaPeliculas = []
    for url in listaURLsPeliculas:
        try:
            openURL = urllib.request.urlopen(url)
            bs = BeautifulSoup(openURL, "lxml")
            res = bs.find("div", class_="results_page").find_all("div", class_=["card", "v4", "tight"])
            listaPeliculas.append(res)
        except Exception as e:
            print(f"Error al abrir la URL {url}: {e}")
    return listaPeliculas

def extraer_datos_peliculas():
    listaPel = get_peliculas()
    listaPeliculas = []
    for tipoPeliculas in listaPel:
        for pelicula in tipoPeliculas:
            linkP = pelicula.find("a")['href']
            linkPel = urlGeneral + linkP
            
            titulo = pelicula.find("div", class_="title").find("a").getText()
            sinopsis = pelicula.find("div", class_="overview").find("p").getText() if pelicula.find("div", class_="overview").find("p") else "No existe sinopsis."

            try:
                openURL2 = urllib.request.urlopen(linkPel)
                bs2 = BeautifulSoup(openURL2, "lxml")
                dur = bs2.find("div", class_=["header_poster_wrapper", "false"]).find("div", class_="facts")
                duracion = dur.find("span", class_="runtime").getText().replace(" ", "") if dur else "No se especifica"
                img_tag = bs2.find("img", class_=["poster", "lazyload"])
                portada = urlGeneral + img_tag.get("data-srcset").split(",")[1][1:-3] if img_tag and img_tag.get("data-srcset") else "default_portada.jpg"

                listaActores = extraer_actores_pelicula(linkPel)
                listaPersonal = extraer_personal_pelicula(linkPel)
                listaGeneros = extraer_generos_pelicula(linkPel)

                listaPeliculas.append([titulo, portada, sinopsis, linkPel, duracion, listaActores, listaPersonal, listaGeneros])
            except Exception as e:
                print(f"Error al extraer datos de la película {titulo}: {e}")
    return listaPeliculas

def extraer_actores_pelicula(url):
    try:
        openURL2 = urllib.request.urlopen(url)
        bs2 = BeautifulSoup(openURL2, "lxml")
        listaActores = []
        actores = bs2.find("div", class_="white_column").find_all("li")[:3]
        for actor in actores:
            if actor.find("img"):
                nombreActor = actor.find("p").find("a").getText()
                srcset = actor.find("img")['srcset'].split(",")[1][1:-3]
                imagen = urlGeneral + srcset
                linkActor = urlGeneral + actor.find("a")['href']
                listaActores.append([nombreActor, imagen, linkActor])
        return listaActores
    except Exception as e:
        print(f"Error al extraer actores de la URL {url}: {e}")
        return []

def extraer_personal_pelicula(urlPelicula):
    try:
        openURL4 = urllib.request.urlopen(urlPelicula)
        bs4 = BeautifulSoup(openURL4, "lxml")
        listaPersonal = []
        gente = bs4.find("ol", class_=["people", "no_image"]).find_all("li")[:3]
        for persona in gente:
            trabajador = persona.find("p").getText()
            puesto = persona.find("p", class_="character").getText() if persona.find("p", class_="character") else "Sin especificar"
            listaPersonal.append([trabajador, puesto])
        return listaPersonal
    except Exception as e:
        print(f"Error al extraer personal de la URL {urlPelicula}: {e}")
        return []

def extraer_generos_pelicula(urlPelicula):
    try:
        openURL5 = urllib.request.urlopen(urlPelicula)
        bs5 = BeautifulSoup(openURL5, "lxml")
        listaGeneros = []
        generos = bs5.find("span", class_="genres").find_all("a")
        for g in generos:
            genero = g.getText()
            listaGeneros.append(genero)
        return listaGeneros
    except Exception as e:
        print(f"Error al extraer géneros de la URL {urlPelicula}: {e}")
        return []

def populateDB():
    num_peliculas = 0
    num_actores = 0
    num_generos = 0
    num_personal = 0

    Pelicula.objects.all().delete()
    Actor.objects.all().delete()
    Genero.objects.all().delete()
    Personal.objects.all().delete()

    listaPeliculas = extraer_datos_peliculas()
    for pelicula in listaPeliculas:
        if not Pelicula.objects.filter(titulo=pelicula[0]).exists():
            # Actores
            for actor in pelicula[5]:
                if not Actor.objects.filter(nombre=actor[0]).exists():
                    Actor.objects.create(nombre=actor[0], foto=actor[1], linkActor=actor[2])
                    num_actores += 1

            # Géneros
            for genero in pelicula[7]:
                if not Genero.objects.filter(nombre=genero).exists():
                    Genero.objects.create(nombre=genero)
                    num_generos += 1

            # Personal
            for personal in pelicula[6]:
                if not Personal.objects.filter(nombre=personal[0]).exists():
                    Personal.objects.create(nombre=personal[0], puesto=personal[1])
                    num_personal += 1

            # Película
            p = Pelicula.objects.create(titulo=pelicula[0], portada=pelicula[1], sinopsis=pelicula[2], linkPelicula=pelicula[3], duracion=pelicula[4])
            p.save()
            for act in pelicula[5]:
                p.actores.add(Actor.objects.get(nombre=act[0]))
            for per in pelicula[6]:
                p.personal.add(Personal.objects.get(nombre=per[0]))
            for gen in pelicula[7]:
                p.generos.add(Genero.objects.get(nombre=gen))

            num_peliculas += 1

    return num_peliculas, num_generos, num_actores, num_personal

def carga(request):
    if request.method == 'POST':
        if 'Aceptar' in request.POST:
            num_peliculas, num_generos, num_actores, num_personal = populateDB()
            mensaje = f"Se han almacenado: {num_peliculas} películas, {num_generos} géneros, {num_actores} actores, {num_personal} trabajadores para películas."
            return render(request, 'cargaBD.html', {'mensaje': mensaje})
        else:
            return redirect("/")
    return render(request, 'confirmacion.html')

def soloNombres(lista):
    return [elemento[0].replace("'", "") for elemento in lista]

def populateWhooshPeliculas():
    schemPeliculas = Schema(idPelicula=NUMERIC(stored=True), titulo=TEXT(stored=True), portada=STORED(), sinopsis=TEXT(stored=True), linkPelicula=TEXT(stored=True), duracion=TEXT(stored=True), actores=KEYWORD(stored=True, commas=True), personal=KEYWORD(stored=True, commas=True), genero=KEYWORD(stored=True, commas=True))

    if os.path.exists("Index"):
        shutil.rmtree("Index")
    os.mkdir("Index")

    ix = create_in("Index", schema=schemPeliculas)
    writer = ix.writer()
    listaPeliculas = extraer_datos_peliculas()
    for numPeliculas, pelicula in enumerate(listaPeliculas, start=1):
        writer.update_document(idPelicula=numPeliculas, titulo=pelicula[0], portada=pelicula[1], sinopsis=pelicula[2], linkPelicula=pelicula[3], duracion=pelicula[4], actores=soloNombres(pelicula[5]), personal=soloNombres(pelicula[6]), genero=pelicula[7])
    writer.commit()

    return len(listaPeliculas)

def cargaWhoosh(request):
    if request.method == 'POST':
        if 'Aceptar' in request.POST:
            numPeliculas = populateWhooshPeliculas()
            mensaje = f"Se han almacenado: {numPeliculas} películas."
            return render(request, 'cargaWhoosh.html', {'mensaje': mensaje})
        else:
            return redirect("/")
    return render(request, 'confirmacion.html')
