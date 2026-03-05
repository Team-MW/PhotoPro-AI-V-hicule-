import { useState } from 'react';
import { Upload, Image as ImageIcon, CheckCircle, Car, ArrowRight, Loader2 } from 'lucide-react';
import axios from 'axios';
import './App.css';

function App() {
    const [file, setFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [processing, setProcessing] = useState(false);
    const [result, setResult] = useState(null);

    const handleDrop = (e) => {
        e.preventDefault();
        const droppedFile = e.dataTransfer.files[0];
        if (droppedFile && droppedFile.type.startsWith('image/')) {
            processFile(droppedFile);
        }
    };

    const handleChange = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile) {
            processFile(selectedFile);
        }
    };

    const processFile = async (selectedFile) => {
        setFile(selectedFile);
        setPreview(URL.createObjectURL(selectedFile));
        setProcessing(true);
        setResult(null);

        const formData = new FormData();
        formData.append('file', selectedFile);

        try {
            // Note: On utilise le proxy de Vite vers http://localhost:8000
            const response = await axios.post('http://localhost:8000/process-image', formData, {
                responseType: 'blob'
            });

            const imageUrl = URL.createObjectURL(response.data);
            setResult(imageUrl);
        } catch (error) {
            console.error('Erreur lors du traitement:', error);
            alert('Erreur lors du traitement de l\'image. Vérifiez que le serveur Python tourne.');
        } finally {
            setProcessing(false);
        }
    };

    return (
        <div className="app-container">
            <header>
                <div className="logo">
                    <Car size={32} color="#3b82f6" />
                    <h1>PhotoPro <span>AI</span></h1>
                </div>
                <p>Sublimez vos annonces véhicules en un clic</p>
            </header>

            <main>
                <div className="process-grid">
                    {/* Section Upload */}
                    <div
                        className={`dropzone ${file ? 'has-file' : ''}`}
                        onDragOver={(e) => e.preventDefault()}
                        onDrop={handleDrop}
                    >
                        {!file ? (
                            <label htmlFor="file-upload" className="upload-label">
                                <div className="icon-circle">
                                    <Upload size={40} />
                                </div>
                                <h3>Glissez votre photo ici</h3>
                                <p>Ou cliquez pour sélectionner un fichier</p>
                                <input id="file-upload" type="file" hidden onChange={handleChange} accept="image/*" />
                            </label>
                        ) : (
                            <div className="preview-container">
                                <img src={preview} alt="Aperçu" className="image-preview" />
                                {processing && (
                                    <div className="overlay">
                                        <Loader2 className="spinner" size={48} />
                                        <p>Détourage par IA en cours...</p>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>

                    <div className="arrow-section">
                        <ArrowRight size={48} className={processing ? 'anim-pulse' : ''} />
                    </div>

                    {/* Section Résultat */}
                    <div className="result-zone">
                        {result ? (
                            <div className="result-container">
                                <img src={result} alt="Résultat" className="image-result" />
                                <div className="success-badge">
                                    <CheckCircle size={20} />
                                    <span>Prêt pour l'annonce</span>
                                </div>
                                <a href={result} download="voiture_pro.jpg" className="download-btn">
                                    Télécharger l'image
                                </a>
                            </div>
                        ) : (
                            <div className="placeholder-result">
                                <ImageIcon size={64} opacity={0.2} />
                                <p>Le résultat apparaîtra ici</p>
                            </div>
                        )}
                    </div>
                </div>
            </main>

            <footer>
                <p>&copy; 2026 PhotoPro Automation - Spécial Garagistes</p>
            </footer>
        </div>
    );
}

export default App;
