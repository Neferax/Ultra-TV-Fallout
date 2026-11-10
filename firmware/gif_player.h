#pragma once

#include <Arduino.h>
#include <TFT_eSPI.h>

// The caller must stop playback before any feed/TLS operation or network action.
bool gifPlayerStart(const char *path, TFT_eSPI &display);
bool gifPlayerTick(uint32_t nowMs);
void gifPlayerStop();
bool gifPlayerIsActive();
size_t gifPlayerDecoderBytes();
