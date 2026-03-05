import os
import sys
from PIL import Image, ImageFilter, ImageOps
from rembg import remove
import numpy as np

# Configuration
DIRECTOIRE_ENTREE = "entree"
DIRECTOIRE_SORTIE = "sortie"
FICHIER_FOND = "fond.jpg"
QUALITE_SORTIE = 90
LARGEUR_CIBLE_RATIO = 0.8  # La voiture occupera 80% de la largeur

def ajouter_ombre(image_voiture, intensite=100, flou=20):
    """Crée une ombre portée légère sous la voiture."""
    # Extraire le masque alpha
    alpha = image_voiture.getchannel('A')
    
    # Créer une image noire pour l'ombre
    ombre = Image.new('L', image_voiture.size, 0)
    # On utilise le masque de la voiture pour définir la forme de l'ombre
    ombre.paste(intensite, mask=alpha)
    
    # Appliquer un flou gaussien pour l'effet d'ombre douce
    ombre = ombre.filter(ImageFilter.GaussianBlur(flou))
    
    # Créer l'image finale de l'ombre (RGBA)
    ombre_rgba = Image.new('RGBA', image_voiture.size, (0, 0, 0, 0))
    # Créer un calque noir pur avec l'alpha flouté
    ombre_couleurs = Image.new('RGBA', image_voiture.size, (0, 0, 0, 255))
    ombre_rgba = Image.composite(ombre_couleurs, Image.new('RGBA', image_voiture.size, (0,0,0,0)), ombre)
    
    return ombre_rgba

def traiter_image(nom_fichier):
    chemin_entree = os.path.join(DIRECTOIRE_ENTREE, nom_fichier)
    chemin_sortie = os.path.join(DIRECTOIRE_SORTIE, os.path.splitext(nom_fichier)[0] + ".jpg")
    
    try:
        print(f"🔄 Traitement de : {nom_fichier}...")
        
        # 1. Charger l'image de la voiture
        image_orig = Image.open(chemin_entree).convert("RGBA")
        
        # 2. Supprimer le fond avec rembg
        print(f"  ✨ Suppression du fond...")
        image_sans_fond = remove(image_orig)
        
        # 3. Recadrer automatiquement autour de la voiture (enlever les zones transparentes inutiles)
        bbox = image_sans_fond.getbbox()
        if bbox:
            image_sans_fond = image_sans_fond.crop(bbox)
        
        # 4. Charger le fond de showroom
        if not os.path.exists(FICHIER_FOND):
            print(f"  ❌ Erreur : Le fichier '{FICHIER_FOND}' est manquant !")
            return

        fond = Image.open(FICHIER_FOND).convert("RGBA")
        fond_w, fond_h = fond.size
        
        # 5. Redimensionnement intelligent
        voiture_w, voiture_h = image_sans_fond.size
        nouvelle_largeur = int(fond_w * LARGEUR_CIBLE_RATIO)
        ratio = nouvelle_largeur / voiture_w
        nouvelle_hauteur = int(voiture_h * ratio)
        
        image_voiture = image_sans_fond.resize((nouvelle_largeur, nouvelle_hauteur), Image.Resampling.LANCZOS)
        
        # 6. Créer l'ombre
        print(f"  👤 Ajout de l'ombre portée...")
        ombre = ajouter_ombre(image_voiture)
        
        # 7. Positionnement (Centré en bas avec une petite marge)
        marge_bas = int(fond_h * 0.05)
        pos_x = (fond_w - nouvelle_largeur) // 2
        pos_y = fond_h - nouvelle_hauteur - marge_bas
        
        # 8. Assemblage final
        # On crée un calque transparent de la taille du fond pour superposer l'ombre un peu décalée
        calque_final = Image.new('RGBA', fond.size, (0, 0, 0, 0))
        
        # On décale l'ombre légèrement vers le bas pour l'effet réaliste
        decalage_ombre = 5
        calque_final.paste(ombre, (pos_x, pos_y + decalage_ombre), ombre)
        calque_final.paste(image_voiture, (pos_x, pos_y), image_voiture)
        
        # Fusionner avec le fond
        resultat = Image.alpha_composite(fond, calque_final)
        
        # 9. Sauvegarde en JPEG haute qualité
        resultat_final = resultat.convert("RGB")
        resultat_final.save(chemin_sortie, "JPEG", quality=QUALITE_SORTIE)
        
        print(f"  ✅ Terminé ! Sauvegardé dans : {chemin_sortie}")

    except Exception as e:
        print(f"  ❌ Erreur lors du traitement de {nom_fichier} : {str(e)}")

def main():
    # Création des dossiers si inexistants
    if not os.path.exists(DIRECTOIRE_SORTIE):
        os.makedirs(DIRECTOIRE_SORTIE)
    
    if not os.path.exists(DIRECTOIRE_ENTREE):
        os.makedirs(DIRECTOIRE_ENTREE)
        print(f"ℹ️ Dossier '{DIRECTOIRE_ENTREE}' créé. Placez vos photos dedans.")
        return

    fichiers = [f for f in os.listdir(DIRECTOIRE_ENTREE) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    
    if not fichiers:
        print(f"ℹ️ Aucune image trouvée dans le dossier '{DIRECTOIRE_ENTREE}'.")
        return

    print(f"🚀 Début du traitement par lot ({len(fichiers)} images)...")
    
    for fichier in fichiers:
        traiter_image(fichier)
    
    print("\n🏁 Mission accomplie ! Toutes les photos sont prêtes.")

if __name__ == "__main__":
    main()
