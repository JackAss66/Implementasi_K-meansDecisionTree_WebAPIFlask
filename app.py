import os
import pandas as pd
from flask import Flask, request, jsonify, render_template
import joblib

# 1. DEFINISIKAN JENIS KACA UNTUK SETIAP CLUSTER
GLASS_TYPES = {
    0: {
        "name": "Building Windows Float Glass",
        "name_id": "Kaca Jendela Bangunan",
        "description": "Kaca dengan kadar Magnesium (Mg) dan Kalsium (Ca) yang cukup tinggi, serta kadar Silikon (Si) yang dominan. Sifat kimiawi ini menghasilkan kaca dengan kejernihan optik yang sangat baik dan stabilitas struktural yang kuat.",
        "characteristics": {
            "Mg": "Tinggi (~3.4%)",
            "Ca": "Sedang (~8.5%)",
            "Ba": "Sangat Rendah (~0.01%)",
            "Si": "Tinggi (~72.8%)"
        }
    },
    1: {
        "name": "Headlamp / Tableware Glass",
        "name_id": "Kaca Lampu Depan / Peralatan Makan",
        "description": "Kaca dengan kadar Barium (Ba) tinggi dan Magnesium (Mg) sangat rendah. Penambahan Barium membuat kaca ini memiliki kemampuan memantulkan dan membiaskan cahaya dengan sangat baik.",
        "characteristics": {
            "Ba": "Tinggi (~1.08%)",
            "Mg": "Sangat Rendah (~0.45%)",
            "Al": "Sedang (~2.16%)",
            "Ca": "Sedang (~8.4%)"
        }
    },
    2: {
        "name": "Tableware / Container Glass",
        "name_id": "Kaca Peralatan Makan / Wadah",
        "description": "Kaca dengan kadar Kalium (K) sangat tinggi dan hampir tidak mengandung Magnesium (Mg) sama sekali. Kandungan Kalium yang tinggi meningkatkan ketahanan kimia dan ketahanan terhadap perubahan suhu ekstrem.",
        "characteristics": {
            "K": "Sangat Tinggi (~6.21%)",
            "Mg": "Nol (0%)",
            "Al": "Tinggi (~3.03%)",
            "Si": "Rendah (~70.6%)"
        }
    },
    3: {
        "name": "Vehicle Windows Float Glass",
        "name_id": "Kaca Jendela Kendaraan",
        "description": "Kaca dengan kadar Kalsium (Ca) sangat tinggi dan nilai Indeks Bias (RI) tertinggi. Kalsium berperan penting dalam meningkatkan kekerasan dan ketahanan fisik kaca terhadap goresan serta benturan.",
        "characteristics": {
            "Ca": "Tinggi (~11.0%)",
            "RI": "Tertinggi (~1.523)",
            "Mg": "Sedang (~2.05%)",
            "Fe": "Tertinggi (~0.09%)"
        }
    }
}

# 2. DEFINISIKAN CLASS PIPELINE (WAJIB ADA SEBELUM MEMUAT .pkl)
class GlassAnalysisPipeline:
    def __init__(self, scaler, kmeans, decision_tree, feature_names):
        self.scaler = scaler
        self.kmeans = kmeans
        self.decision_tree = decision_tree
        self.feature_names = feature_names

    def predict(self, input_data_dict):
        # Ubah input dictionary menjadi DataFrame dengan urutan kolom yang benar
        df_input = pd.DataFrame([input_data_dict], columns=self.feature_names)
        
        # Prediksi menggunakan K-Means (data harus di-scaling dulu)
        scaled_data = self.scaler.transform(df_input)
        kmeans_cluster = int(self.kmeans.predict(scaled_data)[0])
        
        # Prediksi menggunakan Decision Tree (menggunakan data asli, tidak perlu scaling)
        dt_cluster = int(self.decision_tree.predict(df_input)[0])
        
        # Dapatkan informasi jenis kaca dari kedua cluster
        kmeans_glass_info = GLASS_TYPES.get(kmeans_cluster, {})
        dt_glass_info = GLASS_TYPES.get(dt_cluster, {})
        
        return {
            "kmeans_cluster": kmeans_cluster,
            "kmeans_glass_type": kmeans_glass_info.get("name", "Unknown"),
            "kmeans_glass_type_id": kmeans_glass_info.get("name_id", "Tidak Diketahui"),
            "kmeans_description": kmeans_glass_info.get("description", ""),
            "kmeans_characteristics": kmeans_glass_info.get("characteristics", {}),
            "decision_tree_cluster": dt_cluster,
            "decision_tree_glass_type": dt_glass_info.get("name", "Unknown"),
            "decision_tree_glass_type_id": dt_glass_info.get("name_id", "Tidak Diketahui"),
            "decision_tree_description": dt_glass_info.get("description", ""),
            "decision_tree_characteristics": dt_glass_info.get("characteristics", {}),
            "message": f"K-Means: Cluster {kmeans_cluster} ({kmeans_glass_info.get('name_id', 'Tidak Diketahui')}) | Decision Tree: Cluster {dt_cluster} ({dt_glass_info.get('name_id', 'Tidak Diketahui')})"
        }

# 3. INISIALISASI FLASK & LOAD MODEL
app = Flask(__name__)

# Deteksi path folder tempat app.py berada
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'glass_full_pipeline.pkl')

try:
    # Muat model (Sekarang Python sudah tahu apa itu GlassAnalysisPipeline)
    pipeline = joblib.load(MODEL_PATH)
    print(f"✅ Model berhasil dimuat!")
    
    # Ambil daftar fitur dari pipeline untuk digunakan di HTML
    FEATURES = pipeline.feature_names
except Exception as e:
    print(f"❌ Error saat memuat model: {e}")
    pipeline = None
    FEATURES = ['RI', 'Na', 'Mg', 'Al', 'Si', 'K', 'Ca', 'Ba', 'Fe'] # Fallback

# 4. ENDPOINT RUTE (ROUTES)
@app.route('/')
def index():
    """Halaman utama dengan form input HTML"""
    return render_template('index.html', features=FEATURES, glass_types=GLASS_TYPES)

@app.route('/predict/form', methods=['POST'])
def predict_form():
    """Endpoint untuk menerima data dari Form HTML"""
    if pipeline is None:
        return jsonify({'success': False, 'error': 'Model tidak tersedia'}), 500
    
    try:
        # Ambil data dari form HTML dan ubah ke float
        data = {feature: float(request.form[feature]) for feature in FEATURES}
        
        # Panggil method predict dari objek pipeline
        result = pipeline.predict(data)
        
        return jsonify({
            'success': True,
            'prediction': result,
            'input_data': data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/predict', methods=['POST'])
def predict_json():
    """Endpoint untuk menerima data via JSON (API Murni)"""
    if pipeline is None:
        return jsonify({'success': False, 'error': 'Model tidak tersedia'}), 500
    
    try:
        data = request.get_json()
        result = pipeline.predict(data)
        
        return jsonify({
            'success': True,
            'prediction': result,
            'input_data': data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/glass-types', methods=['GET'])
def get_glass_types():
    """Endpoint untuk mendapatkan daftar semua jenis kaca"""
    return jsonify({
        'success': True,
        'glass_types': GLASS_TYPES
    })

@app.route('/api/info', methods=['GET'])
def api_info():
    """Endpoint untuk mendapatkan informasi API"""
    return jsonify({
        'api_name': 'Glass Classification API',
        'version': '1.0',
        'description': 'API untuk klasifikasi jenis kaca berdasarkan komposisi kimia menggunakan K-Means dan Decision Tree',
        'features': FEATURES,
        'endpoints': {
            '/': 'GET - Halaman utama',
            '/predict': 'POST - Prediksi dengan JSON',
            '/predict/form': 'POST - Prediksi dengan form',
            '/glass-types': 'GET - Daftar jenis kaca',
            '/api/info': 'GET - Informasi API'
        }
    })

# 5. JALANKAN SERVER
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)