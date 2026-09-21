---
name: Coimbatore Urban Growth Intelligence
description: Evidence-led GIS and ML analysis dashboard
colors:
  survey-ink: "#172b33"
  action-teal: "#115d62"
  mineral-paper: "#edf0e8"
  paper-wash: "#e2e9df"
  field-surface: "#f9faf5"
  rule-line: "#b4c2b8"
typography:
  body:
    fontFamily: "system-ui, sans-serif"
rounded:
  panel: "14px"
  control: "8px"
spacing:
  panel: "1.25rem"
components:
  button-primary:
    backgroundColor: "{colors.action-teal}"
    textColor: "#ffffff"
    rounded: "{rounded.control}"
---

# Design System: Coimbatore Urban Growth Intelligence

## Overview

**Creative North Star: "The Surveyor’s Field Sheet"**

The dashboard uses mineral paper, exact rules and deep survey ink to make analytical evidence feel inspectable rather than promotional. Its restrained, high-legibility treatment supports long research sessions and cautious interpretation.

**Key Characteristics:** calm field surfaces; single functional teal action; evidence before prediction.

## Colors

The palette is a restrained paper-and-ink system with teal reserved for actions and completion.

**The Evidence Rule.** Use teal for interactive action and verified completion only; probability colours belong to rendered analytical layers, not general UI chrome.

## Typography

**Body Font:** system UI sans-serif.

**Character:** Compact, plain-language research interface typography with hierarchy carried by size and weight rather than decorative display treatment.

## Layout

The dashboard has a 1320px maximum reading canvas with generous top breathing room. The primary map uses a 1.6:1 split beside run state; it collapses naturally in Streamlit’s narrow layout.

## Elevation & Depth

Depth is conveyed through a pale field surface and a single fine rule; no shadow vocabulary is used.

## Shapes

Analytical panels use gently rounded 14px corners. Primary actions use a tighter 8px radius.

## Components

### Buttons

- **Primary:** solid action teal with white text and an 8px radius.

### Cards / Containers

- **Background:** field-surface; **Border:** one-pixel rule-line; **Corner Style:** 14px.

## Do's and Don'ts

### Do:
- **Do** make data provenance and analysis state visible before interpretation.
- **Do** label modelled probability as susceptibility, not a guarantee.

### Don't:
- **Don't** use UI colour to imply a model result is a policy recommendation.
- **Don't** introduce decorative chart cards in place of the map or actual metrics.
