import logging

import azure.functions as func

app = func.FunctionApp()

@app.timer_trigger(schedule="0 * * * * 6", arg_name="myTimer", run_on_startup=True,
              use_monitor=False) 
def receipt_ingestion(myTimer: func.TimerRequest) -> None:

    try:
        print("Receipt ingestion run started.")
    except Exception:
        logging.exception("Receipt ingestion run failed.")

