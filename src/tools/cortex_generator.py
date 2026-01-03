import numpy as np
import os
import json
import random

class CharLSTM:
    def __init__(self, hidden_size=128, learning_rate=1e-1):
        self.hidden_size = hidden_size
        self.learning_rate = learning_rate
        self.vocab = []
        self.char_to_ix = {}
        self.ix_to_char = {}
        self.vocab_size = 0
        
        # Model Parameters (Weights)
        self.params = {}
        self.memory_dir = "memory_data"
        self.model_path = os.path.join(self.memory_dir, "rnn_weights.npy")
        self.vocab_path = os.path.join(self.memory_dir, "rnn_vocab.json")

    def initialize_weights(self):
        """ Initialize random weights """
        H = self.hidden_size
        V = self.vocab_size
        std = 1.0 / np.sqrt(H)
        
        self.params = {
            "Wf": np.random.randn(H, H + V) * std,
            "bf": np.zeros((H, 1)),
            "Wi": np.random.randn(H, H + V) * std,
            "bi": np.zeros((H, 1)),
            "Wc": np.random.randn(H, H + V) * std,
            "bc": np.zeros((H, 1)),
            "Wo": np.random.randn(H, H + V) * std,
            "bo": np.zeros((H, 1)),
            "Wy": np.random.randn(V, H) * std,
            "by": np.zeros((V, 1))
        }

    def resize_weights(self, new_vocab):
        """ Neuroplasticity: Expand brain capacity for new words """
        old_vocab = self.vocab
        new_chars = [c for c in new_vocab if c not in old_vocab]
        if not new_chars: return

        print(f"🧠 Expanding Cortex: +{len(new_chars)} new characters.")
        
        # Map old indices to new indices to preserve knowledge?
        # Actually, if we just append new chars to the end, old indices stay valid?
        # load_data currently sorts chars. This breaks index alignment!
        # CRITICAL FIX: Vocabulary must be Append-Only or we need a migration map.
        # For simplicity, let's keep it sorted but we must migrate weights.
        # This is complex. 
        # Simpler approach: Append-Only Vocabulary.
        pass # Logic handled in load_data now
        
    def load_data(self, data):
        """ Build Vocabulary (Append Only for Stability) """
        # Load existing vocab first
        if not self.vocab and os.path.exists(self.vocab_path):
             try:
                 with open(self.vocab_path, 'r', encoding='utf-8') as f:
                     self.vocab = json.load(f)
             except: pass

        unique_chars = sorted(list(set(data)))
        new_chars = [c for c in unique_chars if c not in self.vocab]
        
        if new_chars:
            print(f"🧠 Neuroplasticity: Integrating {len(new_chars)} new symbols.")
            old_size = len(self.vocab)
            self.vocab.extend(new_chars) # Append to end to preserve old indices
            self.vocab_size = len(self.vocab)
            self.char_to_ix = {ch: i for i, ch in enumerate(self.vocab)}
            self.ix_to_char = {i: ch for i, ch in enumerate(self.vocab)}
            
            # Resize Weights if they exist
            if self.params:
                self._expand_matrices(old_size, self.vocab_size)
        else:
             # Just rebuild mapping
             self.vocab_size = len(self.vocab)
             self.char_to_ix = {ch: i for i, ch in enumerate(self.vocab)}
             self.ix_to_char = {i: ch for i, ch in enumerate(self.vocab)}

        # Load weights if not loaded
        if not self.params and os.path.exists(self.model_path):
             try:
                 loaded = np.load(self.model_path, allow_pickle=True).item()
                 # Check dimension match
                 if loaded["Wxh"].shape[1] == self.vocab_size:
                     self.params = loaded
                     print("🧠 Weights Restored.")
                 else:
                     print("⚠️ Vocab/Weight Mismatch. Re-initializing or Padding?")
                     # If mismatch, we might need to pad loaded weights?
                     # For now, let's assume Append-Only keeps it safe.
                     # If loaded is smaller, pad it.
                     saved_v = loaded["Wxh"].shape[1]
                     if saved_v < self.vocab_size:
                         print(f"🔧 Pachting weights {saved_v} -> {self.vocab_size}")
                         self.params = loaded
                         self._expand_matrices(saved_v, self.vocab_size)
                     else:
                         self.params = loaded
             except Exception as e:
                 print(f"Load Error: {e}")
                 self.initialize_weights()
        elif not self.params:
             self.initialize_weights()

        return True

    def _expand_matrices(self, old_v, new_v):
        """ Expand weight matrices to accommodate new vocabulary """
        # Wxh: (H, V) -> (H, V_new)
        # Why: (V, H) -> (V_new, H)
        # by: (V, 1) -> (V_new, 1)
        added = new_v - old_v
        std = 1.0 / np.sqrt(self.hidden_size)
        
        # Wxh: Pad columns
        new_cols = np.random.randn(self.hidden_size, added) * std
        self.params["Wxh"] = np.hstack((self.params["Wxh"], new_cols))
        
        # Why: Pad rows
        new_rows = np.random.randn(added, self.hidden_size) * std
        self.params["Why"] = np.vstack((self.params["Why"], new_rows))
        
        # by: Pad rows
        new_bias = np.zeros((added, 1))
        self.params["by"] = np.vstack((self.params["by"], new_bias))
        
    def train(self, data, epochs=1000, seq_length=25):
        print(f"🎓 Training SimpleRNN on {len(data):,} chars for {epochs} steps...")
        print(f"📊 Progress: ", end="", flush=True)
        if not self.params: self.initialize_weights()
        
        m_params = {k: np.zeros_like(v) for k, v in self.params.items()}
        p = 0
        h_prev = np.zeros((self.hidden_size, 1))
        
        progress_interval = max(1, epochs // 20)  # Show 20 progress markers
        last_loss = 0
        
        for i in range(epochs):
            if p + seq_length + 1 >= len(data) or p == 0:
                h_prev = np.zeros((self.hidden_size, 1))
                p = 0

            inputs = [self.char_to_ix[ch] for ch in data[p:p+seq_length] if ch in self.char_to_ix]
            targets = [self.char_to_ix[ch] for ch in data[p+1:p+seq_length+1] if ch in self.char_to_ix]
            
            if len(inputs) < seq_length: 
                p = 0
                continue

            xs, hs, ps = {}, {}, {}
            hs[-1] = np.copy(h_prev)
            loss = 0

            # Forward
            for t in range(len(inputs)):
                xs[t] = np.zeros((self.vocab_size, 1))
                xs[t][inputs[t]] = 1
                
                # RNN Step
                h_next = np.tanh(np.dot(self.params["Wxh"], xs[t]) + np.dot(self.params["Whh"], hs[t-1]) + self.params["bh"])
                y = np.dot(self.params["Why"], h_next) + self.params["by"]
                hs[t] = h_next
                ps[t] = self.softmax(y)
                
                loss += -np.log(ps[t][targets[t], 0])

            # Backward
            dparams = {k: np.zeros_like(v) for k, v in self.params.items()}
            dh_next = np.zeros_like(h_prev)
            
            for t in reversed(range(len(inputs))):
                dy = np.copy(ps[t])
                dy[targets[t]] -= 1
                
                dparams["Why"] += np.dot(dy, hs[t].T)
                dparams["by"] += dy
                
                dh = np.dot(self.params["Why"].T, dy) + dh_next
                dhraw = (1 - hs[t] * hs[t]) * dh
                
                dparams["bh"] += dhraw
                dparams["Wxh"] += np.dot(dhraw, xs[t].T)
                dparams["Whh"] += np.dot(dhraw, hs[t-1].T)
                
                dh_next = np.dot(self.params["Whh"].T, dhraw)

            # Update (Adagrad) with Gradient Clipping
            for k, param in self.params.items():
                np.clip(dparams[k], -5, 5, out=dparams[k]) # Prevent explosion
                m_params[k] += dparams[k] * dparams[k]
                param += -self.learning_rate * dparams[k] / np.sqrt(m_params[k] + 1e-8)

            p += seq_length
            
            # Progress display
            if i % progress_interval == 0:
                percent = int((i / epochs) * 100)
                print(f"▓", end="", flush=True)
                last_loss = loss
            
            h_prev = hs[len(inputs)-1]
        
        print(f" ✅ Done! (Final Loss: {last_loss:.2f})")
        self.save()

    def save(self):
        np.save(self.model_path, self.params)
        with open(self.vocab_path, 'w', encoding='utf-8') as f:
            json.dump(self.vocab, f)

class SimpleRNN(CharLSTM):
    """ Vanilla RNN for simplicity and 'Glitchy' aesthetic """
    def initialize_weights(self):
        H = self.hidden_size
        V = self.vocab_size
        std = 1.0 / np.sqrt(H)
        self.params = {
            "Wxh": np.random.randn(H, V) * std,
            "Whh": np.random.randn(H, H) * std,
            "Why": np.random.randn(V, H) * std,
            "bh": np.zeros((H, 1)),
            "by": np.zeros((V, 1))
        }
        
    def step(self, x, h):
        h = np.tanh(np.dot(self.params["Wxh"], x) + np.dot(self.params["Whh"], h) + self.params["bh"])
        y = np.dot(self.params["Why"], h) + self.params["by"]
        return y, h

    def softmax(self, x):
        """ Stable softmax """
        e_x = np.exp(x - np.max(x))
        return e_x / np.sum(e_x)

    def _expand_matrices(self, old_v, new_v):
        """ Expand Vanilla RNN matrices """
        added = new_v - old_v
        std = 1.0 / np.sqrt(self.hidden_size)
        
        # Wxh: (H, V) -> (H, V_new) -- Pad columns
        new_cols = np.random.randn(self.hidden_size, added) * std
        self.params["Wxh"] = np.hstack((self.params["Wxh"], new_cols))
        
        # Why: (V, H) -> (V_new, H) -- Pad rows
        new_rows = np.random.randn(added, self.hidden_size) * std
        self.params["Why"] = np.vstack((self.params["Why"], new_rows))

        # by: (V, 1) -> (V_new, 1) -- Pad rows
        new_bias = np.zeros((added, 1))
        self.params["by"] = np.vstack((self.params["by"], new_bias))
        print(f"🔧 SimpleRNN Matrix Expanded: V={old_v}->{new_v}")

    def train(self, data, epochs=1000, seq_length=25):
        print(f"🎓 Training SimpleRNN on {len(data)} chars for {epochs} steps...")
        if not self.params: self.initialize_weights()

        m_params = {k: np.zeros_like(v) for k, v in self.params.items()}
        p = 0
        h_prev = np.zeros((self.hidden_size, 1))
        
        progress_interval = max(1, epochs // 10)

        for i in range(epochs):
            if p + seq_length + 1 >= len(data) or p == 0:
                h_prev = np.zeros((self.hidden_size, 1))
                p = 0

            # Safe Input Slice
            input_chars = data[p:p+seq_length]
            target_chars = data[p+1:p+seq_length+1]
            
            # Skip if data end is weird
            if len(input_chars) != len(target_chars):
                p = 0
                continue

            inputs = [self.char_to_ix[ch] for ch in input_chars if ch in self.char_to_ix]
            targets = [self.char_to_ix[ch] for ch in target_chars if ch in self.char_to_ix]

            # Re-check length after filtering unknown chars
            if len(inputs) < 2:
                p += seq_length
                continue

            xs, hs, ps = {}, {}, {}
            hs[-1] = np.copy(h_prev)
            loss = 0

            # Forward
            for t in range(len(inputs)):
                xs[t] = np.zeros((self.vocab_size, 1))
                xs[t][inputs[t]] = 1
                
                # RNN Step
                h_next = np.tanh(np.dot(self.params["Wxh"], xs[t]) + np.dot(self.params["Whh"], hs[t-1]) + self.params["bh"])
                y = np.dot(self.params["Why"], h_next) + self.params["by"]
                hs[t] = h_next
                ps[t] = self.softmax(y)
                
                loss += -np.log(ps[t][targets[t], 0])

            # Backward
            dparams = {k: np.zeros_like(v) for k, v in self.params.items()}
            dh_next = np.zeros_like(h_prev)
            
            for t in reversed(range(len(inputs))):
                dy = np.copy(ps[t])
                dy[targets[t]] -= 1
                
                dparams["Why"] += np.dot(dy, hs[t].T)
                dparams["by"] += dy
                
                dh = np.dot(self.params["Why"].T, dy) + dh_next
                dhraw = (1 - hs[t] * hs[t]) * dh
                
                dparams["bh"] += dhraw
                dparams["Wxh"] += np.dot(dhraw, xs[t].T)
                dparams["Whh"] += np.dot(dhraw, hs[t-1].T)
                
                dh_next = np.dot(self.params["Whh"].T, dhraw)

            # Update (Adagrad) with Gradient Clipping
            for k, param in self.params.items():
                np.clip(dparams[k], -5, 5, out=dparams[k]) # Prevent Explosion
                m_params[k] += dparams[k] * dparams[k]
                param += -self.learning_rate * dparams[k] / np.sqrt(m_params[k] + 1e-8)

            p += seq_length
            if i % progress_interval == 0:
                print(f"Iter {i}, Loss: {loss:.4f}")
            
            h_prev = hs[len(inputs)-1]
        
        self.save()

    def generate(self, seed_text, length=50, temperature=1.0):
        """ Generate text with temperature """
        if not self.vocab: return "..."
        
        # Warmup
        h = np.zeros((self.hidden_size, 1))
        
        # Seed input if known
        last_ix = 0
        for ch in seed_text:
            if ch in self.char_to_ix:
                x = np.zeros((self.vocab_size, 1))
                x[self.char_to_ix[ch]] = 1
                _, h = self.step(x, h)
                last_ix = self.char_to_ix[ch]
        
        # Generate
        output = seed_text
        x = np.zeros((self.vocab_size, 1))
        x[last_ix] = 1
        
        for _ in range(length):
            y, h = self.step(x, h)
            
            # Sampling with Temperature
            # y is logits. y / temp
            p = self.softmax(y / max(0.1, temperature)).ravel()
            
            ix = np.random.choice(range(self.vocab_size), p=p)
            ch = self.ix_to_char[ix]
            
            output += ch
            
            x = np.zeros((self.vocab_size, 1))
            x[ix] = 1
            
            # Stop condition? (EOS char not defined, so just length)
            if ch in ["。", "!", "?", "！", "？"] and len(output) > 20: 
                 break
                 
        return output
