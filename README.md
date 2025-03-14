# IGF-1 Measurement Adjustment Calculator

A web-based calculator tool to help physicians adjust IGF-1 measurements based on timing after Ngenla injection.

## Purpose

This application helps physicians adjust IGF-1 measurements based on the time elapsed since injection. For optimal measurement accuracy, Day 4 sampling (96-108 hours) is recommended, but this calculator can adjust values taken outside this window.

## Features

- Anonymous usage (no physician or patient data stored)
- Two input methods:
  - Hours since injection
  - Date/time selection with graphical pickers
- Support for both measurement units:
  - ng/mL (positive values)
  - SDS (supports negative values)
- Mobile-friendly interface with special consideration for entering negative values
- Reference adjustment table included for transparency

## How It Works

The calculator implements established pharmacokinetic adjustment factors to normalize IGF-1 values measured at various intervals after injection. It applies different multipliers for ng/mL values or addition/subtraction factors for SDS values based on a standardized reference table.

## Usage

Simply visit the live calculator at: [https://endokidz.github.io/IGF-1_Ngenla_time/](https://endokidz.github.io/IGF-1_Ngenla_time/)

No installation required - the tool runs in any modern web browser.

## Disclaimer

This tool is for healthcare professional use only. No patient data is stored. Always use clinical judgment when interpreting adjusted values.
