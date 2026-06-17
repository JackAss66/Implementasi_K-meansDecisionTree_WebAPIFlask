document.getElementById('glassForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const btn = document.getElementById('submitBtn');
    const resultDiv = document.getElementById('result');
    btn.disabled = true;
    btn.innerHTML = `<svg class="animate-spin h-5 w-5 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> Memproses...`;

    const formData = Object.fromEntries(new FormData(this).entries());
    const data = {};
    for (let key in formData) data[key] = parseFloat(formData[key]);

    try {
        const res = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await res.json();

        if (result.success) {
            resultDiv.classList.remove('hidden');
            resultDiv.innerHTML = `
                <h3 class="text-xl font-bold mb-4 text-green-600">✅ Hasil Prediksi Berhasil</h3>
                <div class="grid md:grid-cols-2 gap-4">
                    <div class="p-4 bg-blue-50 rounded-lg border border-blue-100">
                        <h4 class="font-semibold text-blue-800 mb-1">🔹 K-Means Clustering</h4>
                        <p class="text-sm">Cluster: <span class="font-bold">${result.prediction.kmeans.cluster}</span></p>
                        <p class="text-sm">Jenis: <span class="font-bold">${result.prediction.kmeans.type}</span></p>
                        <p class="text-xs text-gray-600 mt-1">${result.prediction.kmeans.description}</p>
                    </div>
                    <div class="p-4 bg-purple-50 rounded-lg border border-purple-100">
                        <h4 class="font-semibold text-purple-800 mb-1">🔹 Decision Tree</h4>
                        <p class="text-sm">Cluster: <span class="font-bold">${result.prediction.decision_tree.cluster}</span></p>
                        <p class="text-sm">Jenis: <span class="font-bold">${result.prediction.decision_tree.type}</span></p>
                        <p class="text-xs text-gray-600 mt-1">${result.prediction.decision_tree.description}</p>
                    </div>
                </div>
                <details class="mt-4">
                    <summary class="cursor-pointer text-sm text-gray-500 hover:text-gray-700">📄 Lihat Data Input</summary>
                    <pre class="mt-2 text-xs bg-gray-100 p-3 rounded">${JSON.stringify(result.input_data, null, 2)}</pre>
                </details>
            `;
        } else {
            resultDiv.classList.remove('hidden');
            resultDiv.innerHTML = `<p class="text-red-600 font-medium">❌ Error: ${result.error}</p>`;
        }
    } catch (err) {
        resultDiv.classList.remove('hidden');
        resultDiv.innerHTML = `<p class="text-red-600 font-medium">❌ Gagal terhubung ke server. Pastikan Flask berjalan.</p>`;
    } finally {
        btn.disabled = false;
        btn.textContent = 'Prediksi';
    }
});

document.getElementById('resetBtn').addEventListener('click', () => {
    document.getElementById('glassForm').reset();
    document.getElementById('result').classList.add('hidden');
    document.getElementById('result').innerHTML = '';
});