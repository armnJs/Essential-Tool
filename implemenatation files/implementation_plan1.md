# Implementation Plan - Floating Features for OmniConvert

Add a set of interactive floating features to OmniConvert, including a Sticky Floating Action Button (FAB) Quick Converter, Global Drag & Drop Overlay, Draggable Floating Mini Converter Window, and Ambient Animated Floating Particles Canvas.

## Proposed Changes

### Frontend Infrastructure (`static/`)

#### [MODIFY] [index.html](file:///d:/Armaan/Essential%20tool/static/index.html)
- Add `#floatingCanvas` element for ambient particle physics.
- Add `#globalDragOverlay` component with animated drop zone, icons, and subtle floating particle feedback.
- Add `#floatingFabBtn` in the bottom-right corner for quick access/toggle.
- Add `#floatingWindow` draggable mini-converter modal widget with controls for drag-header, minimize, close, instant format selection, conversion progress, and download button.

#### [MODIFY] [style.css](file:///d:/Armaan/Essential%20tool/static/css/style.css)
- Add CSS styling for ambient canvas layout and glowing orb visuals.
- Add CSS styling for `.global-drag-overlay` glassmorphic full-viewport overlay with backdrop blur, hover ripples, and target pulsing animations.
- Add CSS styling for `.floating-fab-btn` with gradient styling, hover elevation, pulse indicator, and viewport pinning.
- Add CSS styling for `.floating-window` container featuring glassmorphism, custom header drag handle, smooth transition, minimize state, compact format pills grid, and action controls.

#### [MODIFY] [app.js](file:///d:/Armaan/Essential%20tool/static/js/app.js)
- Implement `initFloatingParticles()` to render responsive floating micro-particles and ambient glowing particles on `#floatingCanvas`.
- Implement `initGlobalDragAndDrop()` to detect viewport dragover events and show `#globalDragOverlay` anywhere on the screen, routing dropped files to conversion.
- Implement `initDraggableFloatingWindow()` for smooth mouse-drag window positioning, bounds clamping, minimize/maximize toggling, and synchronization with the main converter state.
- Implement FAB scroll observer to show/hide quick action floating button.

## Verification Plan

### Automated Tests
- Run `python -m pytest test_converters.py` to ensure backend logic is untouched and tests pass.
- Run `python run_full_suite.py` to verify full conversion engine integrity.

### Manual Verification
- Test drag & drop onto global overlay.
- Test dragging the floating mini converter window around the screen.
- Test FAB button toggle and minimize/close interactions.
- Test file selection and conversion via the floating mini converter window.
- Verify light and dark mode styling compatibility.
