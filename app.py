from flask import Flask, request, jsonify, render_template
import os
import tempfile
from services.data_service import DataService
from services.vector_service import VectorService
from services.recommendation_service import RecommendationService
from services.ocr_service import OCRService
from services.cnn_service import CNNService
from services.pinecone_service import PineconeService

app = Flask(__name__)
data_service = DataService()
vector_service = VectorService(data_service.get_products()["Description"].tolist(), metric="cosine")
reco_service = RecommendationService(data_service, vector_service)
ocr_service = OCRService()
cnn_service = CNNService()
pinecone_service = None
try:
    df_init = data_service.get_products()
    mat = vector_service.matrix.toarray().tolist()
    ids = df_init["StockCode"].astype(str).tolist()
    pinecone_service = PineconeService(index_name="products-index", dimension=len(mat[0]))
    if pinecone_service and pinecone_service.index is not None:
        meta = [{"Description": d} for d in df_init["Description"].astype(str).tolist()]
        pinecone_service.upsert_vectors(ids, mat, meta)
except Exception:
    pinecone_service = None

@app.route('/product-recommendation', methods=['POST'])
def product_recommendation():
    """
    Endpoint for product recommendations based on natural language queries.
    Input: Form data containing 'query' (string).
    Output: JSON with 'products' (array of objects) and 'response' (string).
    """
    query = request.form.get('query', '')
    if pinecone_service and pinecone_service.index is not None:
        q_vec = vector_service.vectorizer.transform([query]).toarray().flatten().tolist()
        matches = pinecone_service.query(q_vec, top_k=5)
        df = data_service.get_products()
        items = []
        for m in matches:
            row = df[df["StockCode"].astype(str) == str(m.id)].iloc[0]
            items.append({
                "StockCode": str(row.get("StockCode", "")),
                "Description": str(row.get("Description", "")),
                "UnitPrice": float(row.get("UnitPrice", 0.0)),
                "Country": str(row.get("Country", "")),
                "similarity": float(getattr(m, "score", 0.0)),
            })
        names = ", ".join(x["Description"] for x in items)
        resp = f"Recommended products: {names}." if items else "No matching products found."
        return jsonify({"products": items, "response": resp})
    result = reco_service.recommend(query)
    return jsonify(result)

@app.route('/ocr-query', methods=['POST'])
def ocr_query():
    """
    Endpoint to process handwritten queries extracted from uploaded images.
    Input: Form data containing 'image_data' (file, base64-encoded image or direct file upload).
    Output: JSON with 'products' (array of objects) and 'response' (string).
    """
    image_file = request.files.get('image_data')
    if not image_file:
        return jsonify({"products": [], "response": "No image uploaded", "extracted_text": ""})
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        image_file.save(tmp.name)
        extracted = ocr_service.extract_text(tmp.name)
    os.unlink(tmp.name)
    result = reco_service.recommend(extracted)
    result["extracted_text"] = extracted
    return jsonify(result)

@app.route('/image-product-search', methods=['POST'])
def image_product_search():
    """
    Endpoint to identify and suggest products from uploaded product images.
    Input: Form data containing 'product_image' (file, base64-encoded image or direct file upload).
    Output: JSON with 'products' (array of objects) and 'response' (string).
    """
    product_image = request.files.get('product_image')
    if not product_image:
        return jsonify({"products": [], "response": "No image uploaded", "class": ""})
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        product_image.save(tmp.name)
        cls = cnn_service.predict_class(tmp.name)
    os.unlink(tmp.name)
    query = cls if cls else "product"
    result = reco_service.recommend(query)
    result["class"] = cls
    return jsonify(result)

@app.route('/sample_response', methods=['GET'])
def sample_response():
    """
    Endpoint to return a sample JSON response for the API.
    Output: JSON with 'products' (array of objects) and 'response' (string).
    """
    return render_template('sample_response.html')

@app.route('/')
def home():
    return render_template('text_query.html')

@app.route('/image-query')
def image_query_page():
    return render_template('image_query.html')

@app.route('/product-image-upload')
def product_image_upload_page():
    return render_template('product_image_upload.html')

if __name__ == '__main__':
    app.run(debug=True)
