import os
import io
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from PIL import Image, ImageFilter
from rembg import remove
import numpy as np

app = FastAPI()

# Configuration CORS pour autoriser le frontend Vite
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FICHIER_FOND = "fond.jpg"
LARGEUR_CIBLE_RATIO = 0.8

def ajouter_ombre(image_voiture, intensite=100, flou=20):
    alpha = image_voiture.getchannel('A')
    ombre = Image.new('L', image_voiture.size, 0)
    ombre.paste(intensite, mask=alpha)
    ombre = ombre.filter(ImageFilter.GaussianBlur(flou))
    ombre_couleurs = Image.new('RGBA', image_voiture.size, (0, 0, 0, 255))
    return Image.composite(ombre_couleurs, Image.new('RGBA', image_voiture.size, (0,0,0,0)), ombre)

@app.post("/process-image")
async def process_image(file: UploadFile = File(...)):
    try:
        # Lire l'image reçue
        contents = await file.read()
        image_orig = Image.open(io.BytesIO(contents)).convert("RGBA")
        
        # 1. Supprimer le fond
        image_sans_fond = remove(image_orig)
        
        # 2. Recadrer auto
        bbox = image_sans_fond.getbbox()
        if bbox:
            image_sans_fond = image_sans_fond.crop(bbox)
        
        # 3. Charger le fond
        if not os.path.exists(FICHIER_FOND):
            raise HTTPException(status_code=500, detail="Fichier fond.jpg manquant sur le serveur")
            
        fond = Image.open(FICHIER_FOND).convert("RGBA")
        fond_w, fond_h = fond.size
        
        # 4. Redimensionnement
        voiture_w, voiture_h = image_sans_fond.size
        ratio = (fond_w * LARGEUR_CIBLE_RATIO) / voiture_w
        nouvelle_w, nouvelle_h = int(voiture_w * ratio), int(voiture_h * ratio)
        image_voiture = image_sans_fond.resize((nouvelle_w, nouvelle_h), Image.Resampling.LANCZOS)
        
        # 5. Ombre
        ombre = ajouter_ombre(image_voiture)
        
        # 6. Assemblage
        pos_x = (fond_w - nouvelle_w) // 2
        pos_y = fond_h - nouvelle_h - int(fond_h * 0.05)
        
        calque_final = Image.new('RGBA', fond.size, (0, 0, 0, 0))
        calque_final.paste(ombre, (pos_x, pos_y + 5), ombre)
        calque_final.paste(image_voiture, (pos_x, pos_y), image_voiture)
        
        resultat = Image.alpha_composite(fond, calque_final).convert("RGB")
        
        # Préparer la réponse
        img_byte_arr = io.BytesIO()
        resultat.save(img_byte_arr, format='JPEG', quality=90)
        img_byte_arr = img_byte_arr.getvalue()
        
        return Response(content=img_byte_arr, media_type="image/jpeg")
        
    except Exception as e:
        print(f"Erreur: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
