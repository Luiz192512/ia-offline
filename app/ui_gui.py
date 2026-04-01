from __future__ import annotations

import queue
import threading
import tkinter as tk

from .assistant import AssistantResponse, OfflineAssistant

APP_BG = "#212121"
SIDEBAR_BG = "#171717"
PANEL_BG = "#2F2F2F"
PANEL_BG_ALT = "#262626"
PANEL_BORDER = "#3A3A3A"
TEXT_PRIMARY = "#F3F3F3"
TEXT_MUTED = "#A8A8A8"
TEXT_SOFT = "#C9C9C9"
TEXT_DARK = "#111111"
ACCENT_BLUE = "#0A84FF"
ACCENT_PURPLE = "#5854C7"
SUCCESS_GREEN = "#1FA971"
WARNING_AMBER = "#C89A2B"
USER_BUBBLE = "#2B2B2B"
ASSISTANT_BUBBLE = "#242424"
SYSTEM_BUBBLE = "#2A2A2A"
FONT_UI = "Segoe UI"


class ScrollableFrame(tk.Frame):
    def __init__(self, parent: tk.Widget, *, bg: str) -> None:
        super().__init__(parent, bg=bg)
        self.canvas = tk.Canvas(
            self,
            bg=bg,
            highlightthickness=0,
            bd=0,
            relief=tk.FLAT,
        )
        self.scrollbar = tk.Scrollbar(
            self,
            orient=tk.VERTICAL,
            command=self.canvas.yview,
            troughcolor=bg,
            bg=PANEL_BG,
            activebackground=PANEL_BG,
            highlightthickness=0,
            bd=0,
        )
        self.inner = tk.Frame(self.canvas, bg=bg)
        self.window_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.inner.bind("<Configure>", self._on_inner_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)

    def _on_inner_configure(self, _event: tk.Event[tk.Misc]) -> None:
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event: tk.Event[tk.Misc]) -> None:
        self.canvas.itemconfigure(self.window_id, width=event.width)

    def _bind_mousewheel(self, _event: tk.Event[tk.Misc]) -> None:
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mousewheel(self, _event: tk.Event[tk.Misc]) -> None:
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event: tk.Event[tk.Misc]) -> None:
        delta = int(-1 * (event.delta / 120))
        self.canvas.yview_scroll(delta, "units")


class PromptComposer:
    def __init__(
        self,
        parent: tk.Widget,
        *,
        placeholder: str,
        submit_text: str,
        on_submit: callable,
    ) -> None:
        self.on_submit = on_submit
        self.frame = tk.Frame(
            parent,
            bg=PANEL_BG,
            highlightthickness=1,
            highlightbackground=PANEL_BORDER,
            bd=0,
        )
        self.frame.grid_columnconfigure(1, weight=1)

        self.left_button = tk.Button(
            self.frame,
            text="+",
            command=self._no_op,
            fg=TEXT_PRIMARY,
            bg=PANEL_BG,
            activebackground=PANEL_BG_ALT,
            activeforeground=TEXT_PRIMARY,
            relief=tk.FLAT,
            bd=0,
            font=(FONT_UI, 18),
            width=2,
            cursor="hand2",
        )
        self.left_button.grid(row=0, column=0, padx=(14, 8), pady=10)

        text_holder = tk.Frame(self.frame, bg=PANEL_BG)
        text_holder.grid(row=0, column=1, sticky="ew", pady=8)
        text_holder.grid_columnconfigure(0, weight=1)

        self.text = tk.Text(
            text_holder,
            height=1,
            wrap=tk.WORD,
            bg=PANEL_BG,
            fg=TEXT_PRIMARY,
            insertbackground=TEXT_PRIMARY,
            relief=tk.FLAT,
            bd=0,
            highlightthickness=0,
            font=(FONT_UI, 12),
            padx=0,
            pady=2,
        )
        self.text.grid(row=0, column=0, sticky="ew")
        self.text.bind("<Return>", self._on_return)
        self.text.bind("<KeyRelease>", self._sync_placeholder)
        self.text.bind("<FocusIn>", self._sync_placeholder)
        self.text.bind("<FocusOut>", self._sync_placeholder)

        self.placeholder = tk.Label(
            text_holder,
            text=placeholder,
            fg=TEXT_MUTED,
            bg=PANEL_BG,
            font=(FONT_UI, 12),
        )
        self.placeholder.place(x=2, y=2)

        actions = tk.Frame(self.frame, bg=PANEL_BG)
        actions.grid(row=0, column=2, padx=(8, 10), pady=8)

        self.mic_button = tk.Button(
            actions,
            text="Mic",
            command=self._no_op,
            fg=TEXT_PRIMARY,
            bg=PANEL_BG,
            activebackground=PANEL_BG_ALT,
            activeforeground=TEXT_PRIMARY,
            relief=tk.FLAT,
            bd=0,
            font=(FONT_UI, 10),
            cursor="hand2",
        )
        self.mic_button.pack(side=tk.LEFT, padx=(0, 6))

        self.submit_button = tk.Button(
            actions,
            text=submit_text,
            command=self.submit,
            fg=TEXT_PRIMARY,
            bg=ACCENT_BLUE,
            activebackground=ACCENT_BLUE,
            activeforeground=TEXT_PRIMARY,
            relief=tk.FLAT,
            bd=0,
            font=(FONT_UI, 10, "bold"),
            padx=12,
            pady=6,
            cursor="hand2",
        )
        self.submit_button.pack(side=tk.LEFT)

        self._sync_placeholder()

    def _no_op(self) -> None:
        return None

    def _on_return(self, _event: tk.Event[tk.Misc]) -> str:
        self.submit()
        return "break"

    def _sync_placeholder(self, _event: tk.Event[tk.Misc] | None = None) -> None:
        if self.get_value():
            self.placeholder.place_forget()
        else:
            self.placeholder.place(x=2, y=2)

    def get_value(self) -> str:
        return self.text.get("1.0", "end-1c").strip()

    def set_value(self, value: str) -> None:
        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", value)
        self._sync_placeholder()

    def clear(self) -> None:
        self.set_value("")

    def focus(self) -> None:
        self.text.focus_set()

    def submit(self) -> None:
        value = self.get_value()
        if value:
            self.on_submit(value)

    def set_enabled(self, enabled: bool) -> None:
        state = tk.NORMAL if enabled else tk.DISABLED
        self.text.configure(state=state)
        self.submit_button.configure(state=state)


class OfflineAssistantGUI:
    def __init__(self, assistant: OfflineAssistant) -> None:
        self.assistant = assistant
        self.result_queue: queue.Queue[tuple[str, AssistantResponse | Exception]] = queue.Queue()
        self.recent_titles = [
            "Melhores GGUF 2026",
            "Prompt IA Offline ChatGPT",
            "Resposta educada simples",
        ]
        self.busy = False

        self.root = tk.Tk()
        self.root.title("IA Offline Portatil")
        self.root.geometry("1440x880")
        self.root.minsize(1180, 720)
        self.root.configure(bg=APP_BG)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        self.status_var = tk.StringVar()
        self.status_pill_var = tk.StringVar()

        self._build_sidebar()
        self._build_main_area()
        self._refresh_status()
        self._refresh_recent_list()
        self._show_home_view()

        self.root.after(150, self._poll_results)

    def _build_sidebar(self) -> None:
        sidebar = tk.Frame(self.root, bg=SIDEBAR_BG, width=260)
        sidebar.grid(row=0, column=0, sticky="nsw")
        sidebar.grid_propagate(False)

        top = tk.Frame(sidebar, bg=SIDEBAR_BG)
        top.pack(fill=tk.X, padx=16, pady=(12, 18))

        logo = tk.Label(
            top,
            text="◎",
            fg=TEXT_PRIMARY,
            bg=SIDEBAR_BG,
            font=(FONT_UI, 20, "bold"),
        )
        logo.pack(side=tk.LEFT)

        compact = tk.Label(
            top,
            text="[]",
            fg=TEXT_MUTED,
            bg=SIDEBAR_BG,
            font=(FONT_UI, 11),
        )
        compact.pack(side=tk.RIGHT, pady=(4, 0))

        nav = tk.Frame(sidebar, bg=SIDEBAR_BG)
        nav.pack(fill=tk.X, padx=10)

        self._sidebar_button(nav, "Novo chat", self._new_chat, primary=True)
        self._sidebar_button(nav, "Buscar em chats", self._focus_current_composer)
        self._sidebar_button(nav, "Imagens", lambda: self._show_info("Imagens nao esta disponivel nesta versao offline."))
        self._sidebar_button(nav, "Aplicativos", lambda: self._show_info("Aplicativos ainda nao foi implementado."))
        self._sidebar_button(nav, "Investigacao", lambda: self._show_info("Investigacao offline pode ser adicionada com mais base local."))
        self._sidebar_button(nav, "Codex", lambda: self._show_info("Modo Codex local disponivel pelo mesmo chat."))

        self._section_label(sidebar, "GPTs", pady=(20, 8))
        gpts = tk.Frame(sidebar, bg=SIDEBAR_BG)
        gpts.pack(fill=tk.X, padx=10)
        self._sidebar_button(gpts, "GPT Wizard (Gandalf) by RDD", lambda: self._prefill_prompt("Atue como um tutor tecnico detalhado."), compact=True)
        self._sidebar_button(gpts, "Explorar GPTs", lambda: self._show_info("Voce pode simular personas editando o system prompt local."), compact=True)

        self._section_label(sidebar, "Projetos", pady=(18, 8))
        projects = tk.Frame(sidebar, bg=SIDEBAR_BG)
        projects.pack(fill=tk.X, padx=10)
        self._sidebar_button(projects, "Novo projeto", lambda: self._prefill_prompt("Monte um plano de projeto offline."), compact=True)
        self._sidebar_button(projects, "Reescrever Texto", lambda: self._prefill_prompt("Reescreva este texto de forma mais clara:"), compact=True)

        self._section_label(sidebar, "Seus chats", pady=(18, 8))
        self.recent_holder = tk.Frame(sidebar, bg=SIDEBAR_BG)
        self.recent_holder.pack(fill=tk.BOTH, expand=True, padx=10)

        footer = tk.Frame(sidebar, bg=SIDEBAR_BG)
        footer.pack(fill=tk.X, side=tk.BOTTOM, padx=14, pady=12)

        user_card = tk.Frame(footer, bg=SIDEBAR_BG)
        user_card.pack(fill=tk.X, pady=(0, 12))

        avatar = tk.Label(
            user_card,
            text="TI",
            fg=TEXT_PRIMARY,
            bg="#184F9C",
            font=(FONT_UI, 9, "bold"),
            width=3,
            pady=8,
        )
        avatar.pack(side=tk.LEFT)

        identity = tk.Frame(user_card, bg=SIDEBAR_BG)
        identity.pack(side=tk.LEFT, padx=10)

        tk.Label(
            identity,
            text="IA Offline Portatil",
            fg=TEXT_PRIMARY,
            bg=SIDEBAR_BG,
            font=(FONT_UI, 10, "bold"),
        ).pack(anchor="w")
        tk.Label(
            identity,
            text="Modo local",
            fg=TEXT_MUTED,
            bg=SIDEBAR_BG,
            font=(FONT_UI, 9),
        ).pack(anchor="w")

        offer = tk.Button(
            footer,
            text="Resgatar oferta",
            command=lambda: self._show_info("Esta versao roda localmente, sem assinatura."),
            fg=TEXT_PRIMARY,
            bg=SIDEBAR_BG,
            activebackground=PANEL_BG,
            activeforeground=TEXT_PRIMARY,
            relief=tk.FLAT,
            bd=1,
            highlightthickness=1,
            highlightbackground=PANEL_BORDER,
            font=(FONT_UI, 10, "bold"),
            pady=10,
            cursor="hand2",
        )
        offer.pack(fill=tk.X)

    def _build_main_area(self) -> None:
        main = tk.Frame(self.root, bg=APP_BG)
        main.grid(row=0, column=1, sticky="nsew")
        main.grid_rowconfigure(1, weight=1)
        main.grid_columnconfigure(0, weight=1)

        header = tk.Frame(main, bg=APP_BG)
        header.grid(row=0, column=0, sticky="ew", padx=28, pady=(16, 12))
        header.grid_columnconfigure(1, weight=1)

        title = tk.Label(
            header,
            text="ChatGPT ▾",
            fg=TEXT_PRIMARY,
            bg=APP_BG,
            font=(FONT_UI, 16, "bold"),
        )
        title.grid(row=0, column=0, sticky="w")

        promo = tk.Label(
            header,
            text="Promocao gratuita",
            fg=TEXT_PRIMARY,
            bg=ACCENT_PURPLE,
            font=(FONT_UI, 10, "bold"),
            padx=16,
            pady=8,
        )
        promo.grid(row=0, column=1)

        header_actions = tk.Frame(header, bg=APP_BG)
        header_actions.grid(row=0, column=2, sticky="e")

        self.status_pill = tk.Label(
            header_actions,
            textvariable=self.status_pill_var,
            fg=TEXT_DARK,
            bg=SUCCESS_GREEN,
            font=(FONT_UI, 9, "bold"),
            padx=10,
            pady=6,
        )
        self.status_pill.pack(side=tk.LEFT, padx=(0, 8))

        tk.Button(
            header_actions,
            text="+",
            command=self._new_chat,
            fg=TEXT_PRIMARY,
            bg=APP_BG,
            activebackground=PANEL_BG,
            activeforeground=TEXT_PRIMARY,
            relief=tk.FLAT,
            bd=0,
            font=(FONT_UI, 14),
            cursor="hand2",
        ).pack(side=tk.LEFT, padx=4)

        tk.Button(
            header_actions,
            text="○",
            command=self._show_status_message,
            fg=TEXT_PRIMARY,
            bg=APP_BG,
            activebackground=PANEL_BG,
            activeforeground=TEXT_PRIMARY,
            relief=tk.FLAT,
            bd=0,
            font=(FONT_UI, 14),
            cursor="hand2",
        ).pack(side=tk.LEFT, padx=4)

        body = tk.Frame(main, bg=APP_BG)
        body.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 18))
        body.grid_rowconfigure(0, weight=1)
        body.grid_columnconfigure(0, weight=1)

        self.home_view = tk.Frame(body, bg=APP_BG)
        self.home_view.grid(row=0, column=0, sticky="nsew")
        self.home_view.grid_rowconfigure(0, weight=1)
        self.home_view.grid_rowconfigure(2, weight=1)
        self.home_view.grid_columnconfigure(0, weight=1)

        hero = tk.Frame(self.home_view, bg=APP_BG)
        hero.grid(row=1, column=0)

        tk.Label(
            hero,
            text="O que tem na agenda de hoje?",
            fg=TEXT_PRIMARY,
            bg=APP_BG,
            font=(FONT_UI, 29),
        ).pack(pady=(0, 34))

        self.home_status = tk.Label(
            hero,
            textvariable=self.status_var,
            fg=TEXT_MUTED,
            bg=APP_BG,
            font=(FONT_UI, 10),
        )
        self.home_status.pack(pady=(0, 20))

        home_input_lane = tk.Frame(hero, bg=APP_BG, width=760, height=76)
        home_input_lane.pack()
        home_input_lane.pack_propagate(False)

        self.home_composer = PromptComposer(
            home_input_lane,
            placeholder="Pergunte alguma coisa",
            submit_text="↑",
            on_submit=self._submit_home_prompt,
        )
        self.home_composer.frame.pack(fill=tk.X, ipadx=10)

        self.chat_view = tk.Frame(body, bg=APP_BG)
        self.chat_view.grid(row=0, column=0, sticky="nsew")
        self.chat_view.grid_rowconfigure(0, weight=1)
        self.chat_view.grid_columnconfigure(0, weight=1)

        self.messages_view = ScrollableFrame(self.chat_view, bg=APP_BG)
        self.messages_view.grid(row=0, column=0, sticky="nsew")

        self.chat_composer_holder = tk.Frame(self.chat_view, bg=APP_BG)
        self.chat_composer_holder.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        self.chat_composer_holder.grid_columnconfigure(0, weight=1)

        composer_wrap = tk.Frame(self.chat_composer_holder, bg=APP_BG)
        composer_wrap.grid(row=0, column=0, padx=42, sticky="ew")
        composer_wrap.grid_columnconfigure(0, weight=1)

        self.chat_composer = PromptComposer(
            composer_wrap,
            placeholder="Pergunte alguma coisa",
            submit_text="Enviar",
            on_submit=self._submit_chat_prompt,
        )
        self.chat_composer.frame.grid(row=0, column=0, sticky="ew")

    def _sidebar_button(
        self,
        parent: tk.Widget,
        text: str,
        command: callable,
        *,
        primary: bool = False,
        compact: bool = False,
    ) -> None:
        bg = PANEL_BG_ALT if primary else SIDEBAR_BG
        button = tk.Button(
            parent,
            text=text,
            command=command,
            anchor="w",
            fg=TEXT_PRIMARY if primary else TEXT_SOFT,
            bg=bg,
            activebackground=PANEL_BG,
            activeforeground=TEXT_PRIMARY,
            relief=tk.FLAT,
            bd=0,
            highlightthickness=0,
            font=(FONT_UI, 10 if compact else 11, "bold" if primary else "normal"),
            padx=12,
            pady=10 if compact else 11,
            cursor="hand2",
        )
        button.pack(fill=tk.X, pady=2)

    def _section_label(self, parent: tk.Widget, text: str, *, pady: tuple[int, int]) -> None:
        tk.Label(
            parent,
            text=text,
            fg="#7AA7E8" if text == "Seus chats" else TEXT_MUTED,
            bg=SIDEBAR_BG,
            font=(FONT_UI, 10),
        ).pack(anchor="w", padx=16, pady=pady)

    def _refresh_recent_list(self) -> None:
        for child in self.recent_holder.winfo_children():
            child.destroy()

        for title in self.recent_titles[:8]:
            button = tk.Button(
                self.recent_holder,
                text=title,
                command=lambda value=title: self._prefill_prompt(value),
                anchor="w",
                fg=TEXT_PRIMARY,
                bg=SIDEBAR_BG,
                activebackground=PANEL_BG,
                activeforeground=TEXT_PRIMARY,
                relief=tk.FLAT,
                bd=0,
                highlightthickness=0,
                font=(FONT_UI, 10),
                padx=6,
                pady=8,
                cursor="hand2",
            )
            button.pack(fill=tk.X)

    def _refresh_status(self, *, busy_text: str | None = None) -> None:
        status = self.assistant.status()
        if busy_text:
            pill_text = busy_text
            pill_bg = WARNING_AMBER
            home_text = "Gerando resposta local..."
        elif status["ready"]:
            pill_text = "Offline pronto"
            pill_bg = SUCCESS_GREEN
            home_text = "Runtime local pronto. Base carregada e modelo ativo."
        else:
            pill_text = "Config incompleta"
            pill_bg = WARNING_AMBER
            home_text = str(status["message"])

        self.status_var.set(home_text)
        self.status_pill_var.set(pill_text)
        self.status_pill.configure(bg=pill_bg)

    def _show_home_view(self) -> None:
        self.chat_view.grid_remove()
        self.home_view.grid()
        self.home_composer.focus()

    def _show_chat_view(self) -> None:
        self.home_view.grid_remove()
        self.chat_view.grid()
        self.chat_composer.focus()

    def _focus_current_composer(self) -> None:
        if self.chat_view.winfo_ismapped():
            self.chat_composer.focus()
        else:
            self.home_composer.focus()

    def _prefill_prompt(self, value: str) -> None:
        if self.chat_view.winfo_ismapped():
            self.chat_composer.set_value(value)
            self.chat_composer.focus()
        else:
            self.home_composer.set_value(value)
            self.home_composer.focus()

    def _new_chat(self) -> None:
        self.assistant.clear()
        for child in self.messages_view.inner.winfo_children():
            child.destroy()
        self.home_composer.clear()
        self.chat_composer.clear()
        self._refresh_status()
        self._show_home_view()

    def _show_info(self, message: str) -> None:
        if not self.chat_view.winfo_ismapped():
            self._show_chat_view()
        self._append_message("system", message)

    def _show_status_message(self) -> None:
        status = self.assistant.status()
        content = (
            f"Pronto: {status['ready']}\n"
            f"Status: {status['message']}\n"
            f"Modelo: {status['model']}\n"
            f"Executavel: {status['executable']}\n"
            f"Base local: {status['knowledge_base']}"
        )
        self._show_info(content)

    def _submit_home_prompt(self, value: str) -> None:
        self.home_composer.clear()
        self._submit_prompt(value)

    def _submit_chat_prompt(self, value: str) -> None:
        self.chat_composer.clear()
        self._submit_prompt(value)

    def _submit_prompt(self, value: str) -> None:
        if self.busy:
            return

        clean = value.strip()
        if not clean:
            return

        self._show_chat_view()
        self._append_recent_title(clean)
        self._append_message("user", clean)
        self._set_busy(True)

        thread = threading.Thread(target=self._run_generation, args=(clean,), daemon=True)
        thread.start()

    def _append_recent_title(self, user_input: str) -> None:
        title = user_input.replace("\n", " ").strip()
        if len(title) > 34:
            title = title[:31].rstrip() + "..."

        if title in self.recent_titles:
            self.recent_titles.remove(title)
        self.recent_titles.insert(0, title)
        self._refresh_recent_list()

    def _append_message(self, role: str, content: str, *, meta: str | None = None) -> None:
        row = tk.Frame(self.messages_view.inner, bg=APP_BG)
        row.pack(fill=tk.X, padx=24, pady=10)

        if role == "user":
            bubble_bg = USER_BUBBLE
            title = "Voce"
            anchor = "e"
            side = tk.RIGHT
        elif role == "assistant":
            bubble_bg = ASSISTANT_BUBBLE
            title = "ChatGPT"
            anchor = "w"
            side = tk.LEFT
        else:
            bubble_bg = SYSTEM_BUBBLE
            title = "Sistema"
            anchor = "w"
            side = tk.LEFT

        bubble = tk.Frame(
            row,
            bg=bubble_bg,
            highlightthickness=1,
            highlightbackground=PANEL_BORDER,
            bd=0,
            padx=18,
            pady=14,
        )
        bubble.pack(side=side, anchor=anchor, padx=(140, 140 if role == "user" else 40))

        tk.Label(
            bubble,
            text=title,
            fg=TEXT_MUTED,
            bg=bubble_bg,
            font=(FONT_UI, 9, "bold"),
        ).pack(anchor="w", pady=(0, 8))

        tk.Label(
            bubble,
            text=content,
            fg=TEXT_PRIMARY,
            bg=bubble_bg,
            justify=tk.LEFT,
            wraplength=760,
            font=(FONT_UI, 11),
        ).pack(anchor="w")

        if meta:
            tk.Label(
                bubble,
                text=meta,
                fg=TEXT_MUTED,
                bg=bubble_bg,
                justify=tk.LEFT,
                wraplength=760,
                font=(FONT_UI, 9),
            ).pack(anchor="w", pady=(10, 0))

        self.root.after(40, lambda: self.messages_view.canvas.yview_moveto(1.0))

    def _set_busy(self, busy: bool) -> None:
        self.busy = busy
        self.home_composer.set_enabled(not busy)
        self.chat_composer.set_enabled(not busy)
        self._refresh_status(busy_text="Gerando..." if busy else None)

    def _run_generation(self, user_input: str) -> None:
        try:
            response = self.assistant.respond(user_input)
            self.result_queue.put(("response", response))
        except Exception as exc:  # noqa: BLE001
            self.result_queue.put(("error", exc))

    def _poll_results(self) -> None:
        try:
            kind, item = self.result_queue.get_nowait()
        except queue.Empty:
            self.root.after(150, self._poll_results)
            return

        self._set_busy(False)

        if kind == "error":
            self._append_message("system", str(item))
        else:
            response = item
            meta = None
            if response.sources:
                names = ", ".join(snippet.path.name for snippet in response.sources)
                meta = f"Fontes locais consultadas: {names}"
            self._append_message("assistant", response.text, meta=meta)

        self.root.after(150, self._poll_results)

    def run(self) -> int:
        self.root.mainloop()
        return 0


def run_gui(assistant: OfflineAssistant) -> int:
    gui = OfflineAssistantGUI(assistant)
    return gui.run()
