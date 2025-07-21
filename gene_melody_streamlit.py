import streamlit as st
import pygame
import tempfile
import os
import time
from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo
from PIL import Image
import requests
from base64 import b64encode

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Gene Melody Player",
    page_icon="favicon.ico",
    layout="centered"
)

# --- Constants ---
BASE_NOTE_MAP = {'A': 60, 'T': 62, 'C': 64, 'G': 67}
INSTRUMENTS = {
    0: "Acoustic Grand Piano", 40: "Violin", 41: "Viola", 56: "Trumpet",
    60: "French Horn", 73: "Flute", 81: "Lead Synth", 89: "New Age Pad"
}

# --- Utility Functions ---
def load_lottie_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def dna_to_midi_file(dna_sequence, filename, bpm=120, program=81):
    midi = MidiFile()
    track = MidiTrack()
    midi.tracks.append(track)
    track.append(Message('program_change', program=program, time=0))
    track.append(MetaMessage('set_tempo', tempo=bpm2tempo(bpm), time=0))
    for base in dna_sequence:
        note = BASE_NOTE_MAP.get(base)
        if note:
            track.append(Message('note_on', note=note, velocity=100, time=0))
            track.append(Message('note_off', note=note, velocity=100, time=200))
    midi.save(filename)

def play_midi_with_pygame(midi_path):
    pygame.init()
    pygame.mixer.init()
    try:
        pygame.mixer.music.load(midi_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
    finally:
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        pygame.quit()

def get_base64_img(image_path):
    with open(image_path, "rb") as img_file:
        return b64encode(img_file.read()).decode()

# --- MAIN ---
def main():
    # --- Header with Centered Logo + Title ---
    icon_base64 = get_base64_img("icon.png")
    st.markdown(
        f"""
        <div style='display: flex; justify-content: center; align-items: center; gap: 12px; margin-top: 10px;'>
            <img src='data:image/png;base64,{icon_base64}' width='50'/>
            <h1 style='margin: 0;'>Gene Melody Player</h1>
        </div>
        <p style='text-align: center;'>Turn your DNA sequence into music 🎼</p>
        """,
        unsafe_allow_html=True
    )

    # Optional: Lottie Animation (optional for extra animation)
    # lottie_url = "https://assets9.lottiefiles.com/packages/lf20_cg3q2mbr.json"
    # lottie_json = load_lottie_url(lottie_url)
    # if lottie_json:
    #     import streamlit_lottie
    #     streamlit_lottie.st_lottie(lottie_json, height=200, key="dna")

    # --- DNA Input & Controls ---
    dna_input = st.text_area("Enter DNA Sequence (A, T, C, G only):")
    bpm = st.slider("Tempo (BPM)", 60, 240, 120)
    instrument_name = st.selectbox("Instrument", [f"{name} ({num})" for num, name in INSTRUMENTS.items()])
    instrument_program = int(instrument_name.split("(")[-1].replace(")", ""))

    # --- Play Button ---
    if st.button("▶ Play DNA Music"):
        dna = ''.join([base for base in dna_input.upper() if base in BASE_NOTE_MAP])
        if not dna:
            st.error("Please enter a valid DNA sequence containing A, T, C, or G.")
            return

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mid") as tmp:
            midi_path = tmp.name
        dna_to_midi_file(dna, midi_path, bpm=bpm, program=instrument_program)

        st.success("Playing music... 🎧")
        try:
            play_midi_with_pygame(midi_path)
        except Exception as e:
            st.error(f"Playback error: {e}")
        finally:
            time.sleep(0.3)
            os.unlink(midi_path)

    # --- Download Button ---
    if st.button("💾 Download MIDI File"):
        dna = ''.join([base for base in dna_input.upper() if base in BASE_NOTE_MAP])
        if not dna:
            st.error("Please enter a valid DNA sequence containing A, T, C, or G.")
            return

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mid") as tmp:
            midi_path = tmp.name
        dna_to_midi_file(dna, midi_path, bpm=bpm, program=instrument_program)

        with open(midi_path, "rb") as f:
            st.download_button("Download MIDI", data=f.read(), file_name="dna_music.mid", mime="audio/midi")
        os.unlink(midi_path)

    # --- Footer ---
    st.markdown(
        "<hr><p style='text-align: center; font-size: 0.9em;'>Made with ❤️ to turn genes into symphonies</p>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
