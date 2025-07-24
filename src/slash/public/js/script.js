import { $, create } from "./utils.js";
window.addEventListener('DOMContentLoaded', init);
class Client {
    constructor() {
        this.socket = null;
        this.functions = {};
        this.onclick = this.onclick.bind(this);
        this.oninput = this.oninput.bind(this);
        this.onchange = this.onchange.bind(this);
        this.onpopstate = this.onpopstate.bind(this);
        window.addEventListener("popstate", this.onpopstate);
    }
    connect() {
        const hostname = window.location.hostname;
        const port = window.location.port;
        this.socket = new WebSocket(`ws://${hostname}:${port}/ws`);
        console.log("Connecting to server ..");
        const client = this;
        this.socket.onopen = function () {
            console.log('Connection established!');
            client.send({
                event: "load",
                url: window.location.href
            });
        };
        const loading = $("slash-loading");
        this.socket.onmessage = async function (event) {
            loading === null || loading === void 0 ? void 0 : loading.remove();
            let message;
            try {
                console.info(`%c${event.data}`, 'color: gray;');
                message = JSON.parse(event.data);
            }
            catch (error) {
                console.error(`Received invalid message from server\nmessage: ${event.data}`);
                Slash.message('error', `<b>Received invalid message from server</b><pre><code>${event.data}</code></pre><span>${error}</span>`, { format: "html" });
                return;
            }
            try {
                await client.handle(message);
            }
            catch (error) {
                Slash.message('error', `<b>Failed to handle message from server</b><pre><code>${event.data}</code></pre><span>${error}</span>`, { format: "html" });
                return;
            }
        };
        this.socket.onerror = function (error) {
            console.log('WebSocket error:', error);
        };
        this.socket.onclose = function () {
            console.log('Connection closed.');
            Slash.message('warning', 'Connection lost! Try reloading the page to reconnect to the server.', { permanent: true });
        };
    }
    async handle(message) {
        const event = message.event;
        if (event == "create") {
            const tag = message.tag;
            if (tag === undefined) {
                const parent = this.getElementById(message.parent);
                parent.append(message.text);
                return;
            }
            const elem = (message.ns !== undefined)
                ? document.createElementNS(message.ns, tag)
                : document.createElement(tag);
            elem.id = message.id;
            this.update(elem, message);
            return;
        }
        if (event == "update") {
            const elem = this.getElementById(message.id);
            this.update(elem, message);
            return;
        }
        if (event == "remove") {
            const elem = this.getElementById(message.id);
            elem.remove();
            return;
        }
        if (event == "clear") {
            const elem = this.getElementById(message.id);
            elem.innerHTML = "";
            return;
        }
        if (event == "html") {
            const elem = this.getElementById(message.id);
            elem.innerHTML = message.html;
            return;
        }
        if (event == "script") {
            const script = message.script;
            eval === null || eval === void 0 ? void 0 : eval(`"use strict";(${script})`);
            return;
        }
        if (event == "function") {
            const name = message.name;
            const args = message.args;
            const body = message.body;
            this.functions[name] = new Function(...args, body);
            return;
        }
        if (event == "execute") {
            const name = message.name;
            const args = message.args;
            const value = this.functions[name](...args);
            if (message.store)
                Slash.store(message.store, value);
            return;
        }
        if (event == "log") {
            const type = message.type;
            const text = message.message;
            const format = message.format || "text";
            console.log(`[${type}] %c${text}`, 'color:rgb(216, 198, 162);');
            Slash.message(type, text, { format: format });
            return;
        }
        if (event == "theme") {
            const theme = message.theme;
            document.body.className = theme;
            window.localStorage.setItem("SLASH_THEME", theme);
            return;
        }
        if (event == "title") {
            document.title = message.title;
            return;
        }
        if (event == "cookie") {
            const name = message.name;
            const value = message.value;
            const days = message.days;
            const date = new Date();
            date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
            const expires = "expires=" + date.toUTCString();
            document.cookie = name + "=" + value + ";" + expires + ";path=/";
            ;
            return;
        }
        if (event == "history") {
            if ("go" in message) {
                window.history.go(message.go);
                return;
            }
            if ("push" in message) {
                window.history.pushState(message.push, "", message.url);
                return;
            }
            if ("replace" in message) {
                window.history.replaceState(message.replace, "", message.url);
                return;
            }
            throw new Error("Invalid history event: missing field `go`, `push` or `replace`.");
        }
        throw new Error(`Unknown event '${event}'`);
    }
    update(elem, message) {
        for (const attr in message) {
            if (attr == "event" || attr == "id" || attr == "tag" || attr == "ns" || attr == "position")
                continue;
            if (attr == "parent") {
                const parent = this.getElementById(message.parent);
                if ("position" in message) {
                    if (Object.values(parent.children).includes(elem))
                        parent.removeChild(elem);
                    const position = message.position;
                    if (position >= parent.children.length) {
                        parent.append(elem);
                    }
                    else {
                        parent.insertBefore(elem, parent.children[position]);
                    }
                }
                else {
                    parent.append(elem);
                }
                continue;
            }
            if (attr == "style") {
                for (const [key, value] of Object.entries(message.style)) {
                    if (value !== null && typeof value !== 'string')
                        throw new Error(`Invalid value for style property ${key}`);
                    elem.style.setProperty(key, value);
                }
                continue;
            }
            if (attr == "onclick") {
                if (message.onclick === true) {
                    elem.addEventListener("click", this.onclick);
                }
                else {
                    elem.removeEventListener("click", this.onclick);
                }
                continue;
            }
            if (attr == "oninput") {
                if (message.oninput === true) {
                    elem.addEventListener('input', this.oninput);
                }
                else {
                    elem.removeEventListener("input", this.oninput);
                }
                continue;
            }
            if (attr == "onchange") {
                if (message.onchange === true) {
                    elem.addEventListener('change', this.onchange);
                }
                else {
                    elem.removeEventListener("change", this.onchange);
                }
                continue;
            }
            if (attr == "text") {
                elem.innerText = message.text;
                continue;
            }
            if (attr == "value") {
                if ('value' in elem) {
                    elem.value = message.value;
                    continue;
                }
            }
            const value = message[attr];
            if (value === null)
                elem.removeAttribute(attr);
            else
                elem.setAttribute(attr, value);
        }
    }
    onclick(event) {
        const elem = event.currentTarget;
        if (elem instanceof HTMLElement) {
            this.send({
                event: "click",
                id: elem.id
            });
            event.stopPropagation();
        }
    }
    oninput(event) {
        const elem = event.currentTarget;
        if (elem !== null && "id" in elem && "value" in elem) {
            this.send({
                event: "input",
                id: elem.id,
                value: elem.value
            });
        }
    }
    onchange(event) {
        const elem = event.currentTarget;
        if (elem !== null && "id" in elem && "value" in elem) {
            this.send({
                event: "change",
                id: elem.id,
                value: elem.value
            });
        }
    }
    onpopstate(event) {
        this.send({
            event: "popstate",
            state: event.state
        });
    }
    send(message) {
        var _a;
        (_a = this.socket) === null || _a === void 0 ? void 0 : _a.send(JSON.stringify(message));
    }
    getElementById(id) {
        const elem = $(id);
        if (elem == null)
            throw new Error(`No element exists with id '${id}'`);
        return elem;
    }
}
class Slash {
    static store(name, value) {
        Slash.values[name] = value;
    }
    static value(name) {
        return Slash.values[name];
    }
    static message(type, message, options = {}) {
        const div = create("div", { class: "message " + type }, create("span", { class: "icon" }));
        if (options.format == "html")
            div.insertAdjacentHTML('beforeend', message);
        else
            div.append(message);
        if (options.permanent !== true) {
            const timeout = options.timeout || 10000;
            setTimeout(() => div.classList.add("remove"), timeout);
            setTimeout(() => div.remove(), timeout + 500);
        }
        $("slash-messages").prepend(div);
    }
}
Slash.values = {};
let client;
function init() {
    window.Slash = Slash;
    Slash.message("warning", "", { timeout: -499 });
    const theme = window.localStorage.getItem("SLASH_THEME");
    if (theme !== null)
        document.body.className = theme;
    client = new Client();
    client.connect();
}
