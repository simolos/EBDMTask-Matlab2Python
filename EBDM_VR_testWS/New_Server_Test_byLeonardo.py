# Run: pip install numpy websockets uvicorn fastapi
# Run uvicorn websocket_server:app --host 127.0.0.1 --port 8765 --log-level info

import asyncio
import random
import keyboard
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import numpy as np
import json

app = FastAPI()

# Permetti tutte le origini (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class WebSocketWithLog():
    def __init__(self, ws: WebSocket, log_path: str):
        self._ws = ws
        self._log_path = log_path
    async def send_json(self, payload):
        with open(self._log_path, 'a') as f:
            f.write(f'{json.dumps(payload)}\n')
        await self._ws.send_json(payload)


# ---- TRIAL 1 EP success
async def run_trial(ws: WebSocketWithLog):
    print("Waiting 1 seconds before trial_beginning...")
    await asyncio.sleep(1)

    # ITI (intertrial interval)
    DurITI = 2
    print("ITI")
    await ws.send_json({"event_": "ITI", "DurITI": DurITI})
    await asyncio.sleep(DurITI)

    # Preparation to the DM phase
    dur_Prep_DM = random.uniform(1, 1.4)
    print("Preparation to the DM phase")
    await ws.send_json({"event_": "PrepDM", "dur_Prep_DM": round(dur_Prep_DM, 2)})
    await asyncio.sleep(dur_Prep_DM)

    # Beginning of the DM phase (Offer Presentation)
    dur_DMphase = 6
    EffortLevel = 0.95
    RewardLevel = 1
    print("DM phase (offer presentation) - max duration 4s")
    await ws.send_json({"event_": "DMphase", "dur_DMphase": dur_DMphase, "Effort": EffortLevel, "Reward": RewardLevel})
    await asyncio.sleep(dur_DMphase)

    # DecisionFeedback phase
    DMFeedback = 1 # yes
    dur_DecisionFeedback = 1
    print("DecisionFeedback")
    await ws.send_json(
        {"event_": "DecisionFeedback", "DMFeedback": DMFeedback, "dur_DecisionFeedback": dur_DecisionFeedback})
    await asyncio.sleep(dur_DecisionFeedback)

    # Preparation to the EP phase
    dur_Prep_EP = random.uniform(1, 1.4)
    print("Preparation to the EP phase")
    await ws.send_json({"event_": "PrepEP", "dur_Prep_EP": round(dur_Prep_EP, 2)})
    await asyncio.sleep(dur_Prep_EP)

    # Beginning of the EP phase
    dur_EPphase = 6
    opening_percentage = 1 - EffortLevel
    print("EP phase")
    await ws.send_json(
        {"event_": "EPphase", "dur_EPphase": round(dur_EPphase, 2), "cursor_pos": round(opening_percentage, 2)})

    # Simulate real door opening
    freq = 120  # Hz (screen sampling rate)
    n_samples = int(dur_EPphase * freq)
    base_values = np.linspace(0.05, 0.97, n_samples)
    noise = np.random.normal(0, 0.01, size=n_samples)  # std dev 0.01
    opening_percentage_values = np.clip(base_values + noise, 0, 1)  # keep between 0 and 1

    for val in opening_percentage_values:
        await ws.send_json({"event_": "EPphase", "dur_EPphase": round(dur_EPphase, 2), "cursor_pos": round(val, 2)})
        await asyncio.sleep(1 / freq)

    # Preparation to the EP Feedback phase
    dur_Prep_EPFeedback = 0.5
    print("Preparation to the EPFeedback phase")
    await ws.send_json({"event_": "PreEPFeedback", "dur_Prep_EPFeedback": dur_Prep_EPFeedback})
    await asyncio.sleep(dur_Prep_EPFeedback)

    # EPFeedback phase
    EPFeedback = 1
    dur_EPFeedback = 1
    print("EPFeedback")
    await ws.send_json({"event_": "EPFeedback", "EPFeedback": EPFeedback, "dur_EPFeedback": dur_EPFeedback})
    await asyncio.sleep(dur_EPFeedback)

    # ITI (intertrial interval)
    DurITI = 2
    print("ITI")
    await ws.send_json({"event_": "ITI", "DurITI": DurITI})
    await asyncio.sleep(DurITI)

    print("Trial finished")
    await ws.send_json({"event_": "EndOfTrial"})

# ---- TRIAL 2 EP anticipation
async def run_trial2(ws: WebSocketWithLog):
    # Wait 1 seconds before starting the trial
    print("Waiting 1 seconds before trial_beginning...")
    await asyncio.sleep(1)

    # ITI (intertrial interval)
    DurITI = 3
    print("ITI")
    await ws.send_json({"event_": "ITI", "DurITI": DurITI})
    await asyncio.sleep(DurITI)

    # Preparation to the DM phase
    dur_Prep_DM = random.uniform(1, 1.4)
    print("Preparation to the DM phase")
    await ws.send_json({"event_": "PrepDM", "dur_Prep_DM": round(dur_Prep_DM, 2)})
    await asyncio.sleep(dur_Prep_DM)

    # Beginning of the DM phase (Offer Presentation)
    dur_DMphase = 4  # max duration
    EffortLevel = 0.95  # porta già aperta al 5%
    RewardLevel = 1     # livello ricompensa
    print("DM phase (offer presentation) - max duration 4s")
    await ws.send_json({"event_": "DMphase", "dur_DMphase": dur_DMphase, "Effort": EffortLevel, "Reward": RewardLevel})
    await asyncio.sleep(dur_DMphase)

    # DecisionFeedback phase
    print("DecisionFeedback")
    DMFeedback = 1  # 1 = yes, 0 = no
    dur_DecisionFeedback = 1
    await ws.send_json({"event_": "DecisionFeedback", "DMFeedback": DMFeedback, "dur_DecisionFeedback": dur_DecisionFeedback})
    await asyncio.sleep(dur_DecisionFeedback)

    # Preparation to the EP phase
    dur_Prep_EP = random.uniform(1, 1.4)
    print("Preparation to the EP phase")
    await ws.send_json({"event_": "PrepEP", "dur_Prep_EP": round(dur_Prep_EP, 2)})
    await asyncio.sleep(dur_Prep_EP)

    # Preparation to the EP Feedback phase
    dur_Prep_EPFeedback = 1  # fisso a 1s
    print("Preparation to the EPFeedback phase")
    await ws.send_json({"event_": "PrepEPFeedback", "dur_Prep_EPFeedback": dur_Prep_EPFeedback})
    await asyncio.sleep(dur_Prep_EPFeedback)

    # EPFeedback phase
    EPFeedback = -1  # -1 anticipation
    dur_EPFeedback = 1
    print("EPFeedback")
    await ws.send_json({"event_": "EPFeedback", "EPFeedback": EPFeedback, "dur_EPFeedback": dur_EPFeedback})
    await asyncio.sleep(dur_EPFeedback)

    # ITI (intertrial interval)
    DurITI = 2
    print("ITI")
    await ws.send_json({"event_": "ITI", "DurITI": DurITI})
    await asyncio.sleep(DurITI)

    print("End of the trial")
    await ws.send_json({"event_": "EndOfTrial"})


@app.websocket("/trials")
async def trials_ws(ws: WebSocket):
    await ws.accept()
    print("[SRV] Client connesso a /trials")

    ws_with_log = WebSocketWithLog(ws, "control_events_byLeonardo.json")

    try:
        while True:
            await run_trial2(ws_with_log) # or run_trial2

            # # Loop asincrono che controlla la tastiera
            # if keyboard.is_pressed("1"):  # premi 1 per trial 1
            #     print("[SRV] Space pressed -> starting trial")
            #     await run_trial(ws)
            #     await asyncio.sleep(0.5)  # debounce per non ripetere subito
            # if keyboard.is_pressed("2"): # premi 2 per trial 2
            #     print("[SRV] Enter pressed -> run_trial2")
            #     await run_trial2(ws)
            #     await asyncio.sleep(0.5)
            # await asyncio.sleep(0.05)
    except Exception as e:
        print(f"[SRV] WebSocket error: {e}")

if __name__ == "__main__":
    uvicorn.run("New_Server_Test_byLeonardo:app", host="0.0.0.0", port=8765, reload=False, log_level="info")
