# this is used inorder to organise our codes
from flask import Blueprint
import controllers.smartapi_controllers as ctrl

smartapi_bp = Blueprint("smartapi", __name__)
# creating a blueprint object named smartapi_bp
# here smartapi is a name of the blueprint used internally

# smartapi_bp.route('/search', methods=['GET'])(ctrl.search_scrip)
# smartapi_bp.route('/ltp_candle', methods=['GET'])(ctrl.ltp)
# smartapi_bp.route('/stock_data', methods=['GET'])(ctrl.stock_data)

smartapi_bp.route('/combined_data', methods=['GET'])(ctrl.combined_data)
smartapi_bp.route('/ticker_data', methods=['GET'])(ctrl.ticker_data)
@smartapi_bp.route('/update_tickers_db', methods=['POST'])
def update_tickers():
    from controllers import smartapi_controller as ctrl
    ctrl.update_ticker_data_to_db()
    return jsonify({"status": "success", "message": "Ticker data updated in DB"})



# smartapi_bp.route('/security-info', methods=['GET'])(ctrl.security_info)
# smartapi_bp.route('/market-data', methods=['GET'])(ctrl.market_data)
# smartapi_bp.route('/option-chain', methods=['GET'])(ctrl.option_chain)
# smartapi_bp.route('/expiry-list', methods=['GET'])(ctrl.expiry_list)
# smartapi_bp.route('/master-contract', methods=['GET'])(ctrl.master_contract)
