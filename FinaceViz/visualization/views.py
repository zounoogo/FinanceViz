
# views.py
from glob import escape
from .forms import CSVUploadForm
import seaborn as sns
import json
import csv
import os
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from django.http import HttpResponse
from django.shortcuts import render
from html import escape
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
import tempfile
from django.shortcuts import render, redirect



def accueil(request):
    return render(request, 'accueil.html')

def contact(request):
    return render(request, 'contact.html')

def about(request):
    return render(request, 'about.html')

def visualize_TabData(request):
    if request.method == 'POST':
        try:
            # Récupération des données du formulaire
            raw_data = request.POST.get('data')
            chart_type = request.POST.get('chart_type')
            filter_column = request.POST.get('filter_column')
            filter_value = request.POST.get('filter_value')

            if not raw_data:
                return render(request, 'visualizationTab.html', {'error': 'Aucune donnée reçue.'})
            if not chart_type:
                return render(request, 'visualizationTab.html', {'error': 'Aucun type de graphique spécifié.'})

            # Conversion des données JSON en DataFrame
            try:
                data = json.loads(raw_data)
            except json.JSONDecodeError:
                return render(request, 'visualizationTab.html', {'error': 'Les données ne sont pas au format JSON valide.'})

            df = pd.DataFrame(data[1:], columns=data[0])
            if 'Date' not in df.columns:
                return render(request, 'visualizationTab.html', {'error': 'La colonne "Date" est manquante dans les données.'})

            # Application des filtres si spécifiés
            if filter_column and filter_value:
                if filter_column not in df.columns:
                    return render(request, 'visualizationTab.html', {'error': f'La colonne "{filter_column}" n\'existe pas dans les données.'})
                try:
                    df = df[df[filter_column].astype(str) == filter_value]
                except Exception as e:
                    return render(request, 'visualizationTab.html', {'error': f'Erreur lors de l\'application du filtre : {str(e)}'})

            # Vérification si le DataFrame n'est pas vide après filtrage
            if df.empty:
                return render(request, 'visualizationTab.html', {'error': 'Aucune donnée ne correspond aux filtres appliqués.'})

            # Génération du graphique
            plt.figure(figsize=(8, 6))
            if chart_type == 'line':
                df.plot(x='Date', kind='line', ax=plt.gca())
            elif chart_type == 'bar':
                df.plot(x='Date', kind='bar', ax=plt.gca())
            elif chart_type == 'pie':
                df.set_index('Date').iloc[0].plot(kind='pie', ax=plt.gca(), autopct='%1.1f%%')
            else:
                return render(request, 'visualizationTab.html', {'error': 'Type de graphique invalide.'})
            plt.tight_layout()

            # Sauvegarder le graphique dans un fichier temporaire
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_image:
                plt.savefig(temp_image.name, format='png')
                temp_image_path = temp_image.name
            plt.close()

            # Convertir le DataFrame en tableau HTML
            table_html = df.to_html(classes='table table-striped')

            # Encodage du graphique pour affichage dans la page HTML
            with open(temp_image_path, "rb") as img_file:
                image_base64 = base64.b64encode(img_file.read()).decode('utf-8')
            os.unlink(temp_image_path)

            return render(request, 'visualizationTab.html', {
                'info': 'Données reçues et graphique généré avec succès.',
                'raw_data': raw_data,
                'chart_type': chart_type,
                'filter_column': filter_column,
                'filter_value': filter_value,
                'graph': image_base64,
                'table_html': table_html,
            })

        except Exception as e:
            return render(request, 'visualizationTab.html', {'error': str(e)})

    return render(request, 'visualizationTab.html')




def visualize_CSVData(request):
    if request.method == 'POST':
        try:
            # Récupération du fichier CSV et des autres champs
            csv_file = request.FILES.get('csv_file')
            chart_type = request.POST.get('chart_type')
            filter_column = request.POST.get('filter_column')
            filter_value = request.POST.get('filter_value')

            if not csv_file:
                return render(request, 'visualizationCSV.html', {'error': 'Aucun fichier CSV n\'a été téléchargé.'})
            if not chart_type:
                return render(request, 'visualizationCSV.html', {'error': 'Aucun type de graphique spécifié.'})

            # Lecture du fichier CSV dans un DataFrame
            try:
                df = pd.read_csv(csv_file)
            except Exception as e:
                return render(request, 'visualizationCSV.html', {'error': f'Erreur lors de la lecture du fichier CSV : {e}'})

            if filter_column and filter_value:
                if filter_column not in df.columns:
                    return render(request, 'visualizationCSV.html', {'error': f'La colonne "{filter_column}" n\'existe pas dans le fichier CSV.'})
                # Appliquer le filtre
                df = df[df[filter_column].astype(str) == filter_value]

            # Vérification si la colonne 'Date' existe
            if 'Date' not in df.columns:
                return render(request, 'visualizationCSV.html', {'error': 'La colonne "Date" est manquante dans les données.'})

            # Génération du graphique
            plt.figure(figsize=(8, 6))
            if chart_type == 'line':
                df.plot(x='Date', kind='line', ax=plt.gca())
            elif chart_type == 'bar':
                df.plot(x='Date', kind='bar', ax=plt.gca())
            elif chart_type == 'pie':
                df.set_index('Date').iloc[0].plot(kind='pie', ax=plt.gca(), autopct='%1.1f%%')
            else:
                return render(request, 'visualizationCSV.html', {'error': 'Type de graphique invalide.'})
            plt.tight_layout()

            # Sauvegarde du graphique dans un fichier temporaire
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_image:
                plt.savefig(temp_image.name, format='png')
                temp_image_path = temp_image.name
            plt.close()

            # Convertir le DataFrame en tableau HTML
            table_html = df.to_html(classes='table table-striped')

            # Génération de PDF si demandé
            if 'download_pdf' in request.POST:
                response = HttpResponse(content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="graph_table.pdf"'

                pdf_canvas = canvas.Canvas(response, pagesize=letter)
                width, height = letter

                # Page 1 : Ajouter le graphique
                pdf_canvas.drawImage(temp_image_path, 50, height - 300, width=500, height=250)
                pdf_canvas.showPage()

                # Page 2 : Ajouter le tableau
                data_for_table = [df.columns.tolist()] + df.values.tolist()
                table = Table(data_for_table)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                table.wrapOn(pdf_canvas, width, height)
                table.drawOn(pdf_canvas, 50, height - 700)

                pdf_canvas.save()
                os.unlink(temp_image_path)  # Supprimer le fichier temporaire
                return response

            # Encodage du graphique pour affichage dans la page HTML
            with open(temp_image_path, "rb") as img_file:
                image_base64 = base64.b64encode(img_file.read()).decode('utf-8')
            os.unlink(temp_image_path)

            return render(request, 'visualizationCSV.html', {
                'info': 'Données reçues et graphique généré avec succès.',
                'chart_type': chart_type,
                'graph': image_base64,
                'table_html': table_html,
            })

        except Exception as e:
            return render(request, 'visualizationCSV.html', {'error': str(e)})

    return render(request, 'visualizationCSV.html')
