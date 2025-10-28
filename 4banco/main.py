import logging
import os
import sys
import traceback

from ai_modules.ai import get_best_move_from_grid
from flask import Flask, jsonify, render_template, request, send_from_directory

sys.path.insert(0, os.path.dirname(__file__))

# ------------------------------
# Cấu hình Flask
# ------------------------------
app = Flask(__name__)

# Logging đầy đủ, in ra console
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

# ------------------------------
# Routes
# ------------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route('/ads.txt')
def ads_txt():
    return send_from_directory('static', 'ads.txt')

@app.route("/ai_move", methods=["POST"])
def ai_move():
    try:
        data = request.get_json(force=True)
        app.logger.debug(f"📩 Nhận request /ai_move: {data}")

        grid = data.get("grid")
        ai_color = data.get("aiColor")
        depth = data.get("depth", 4)

        if not grid or not ai_color:
            msg = "Thiếu grid hoặc aiColor"
            app.logger.error(f"⚠️ {msg}")
            return jsonify({"status": "error", "message": msg}), 400

        # Debug chi tiết grid
        app.logger.debug(f"[DEBUG] Grid trước khi gửi AI: {grid}")
        app.logger.info(f"🧠 AI đang tính nước đi... màu={ai_color}, depth={depth}")

        # Gọi hàm AI
        move = get_best_move_from_grid(
            grid, 
            ai_color, 
            requested_depth=depth,
            time_limit=10
        )

        if move is None:
            app.logger.warning("⚠️ AI trả về None, không tìm được nước đi hợp lệ.")
        else:
            app.logger.info(f"✅ AI trả về move: {move}")

        return jsonify({"status": "ok", "move": move})

    except Exception as e:
        tb = traceback.format_exc()
        app.logger.error(f"💥 Lỗi xử lý /ai_move: {e}\n{tb}")
        return jsonify({"status": "error", "message": str(e), "trace": tb}), 500

# ------------------------------
# Entry point local (dev only)
# ------------------------------
if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5000))
    print(f"🚀 Flask development server khởi động tại port {PORT} (DEBUG ON)...")
    app.run(host="0.0.0.0", port=PORT, debug=True)