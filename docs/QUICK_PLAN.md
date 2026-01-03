# QUICK_PLAN: Fix Respiration Logic Indentation

## 1. Context
- **Issue**: `IndentationError: unexpected indent` in `body.py` at line 257.
- **Cause**: The code block for "Digital Respiration System" was pasted with incorrect indentation relative to the `while self.is_alive:` loop.
- **Goal**: Correct the indentation and ensure the respiration logic runs smoothly within the animation loop.

## 2. Risk Check
- **Scope**: `body.py` only.
- **Risk**: Low. Purely syntax/logic fix within a single method.

## 3. Core Implementation
- **File**: `c:\Users\Humin\.gemini\antigravity\scratch\new-ai-project\body.py`
- **Action**: 
    - Adjust indentation of lines 257-300 to match the `while` loop body.
    - Ensure `pulse_phase` logic is correctly placed.

## 4. Verification
- **Command**: `python main.py`
- **Success Criteria**: 
    - Application starts without error.
    - Ghost orb pulses/breathes visually.
    - No crash on heartbeat update.

## 5. Stop Rule
- If fixing indentation reveals further logic errors, revert to previous working state.
