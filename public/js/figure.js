"use strict";
class Graph {
    constructor(pts, options) {
        this.pts = pts;
        this.options = options;
    }
}
class Scatter {
    constructor(pts, options) {
        this.pts = pts;
        this.options = options;
    }
}
class Figure {
    constructor(canvas, options = {}) {
        this.canvas = canvas;
        this.ctx = this.canvas.getContext('2d');
        this.width = canvas.width;
        this.height = canvas.height;
        this.view = { top: 1.0, bottom: 0.0, left: 0.0, right: 1.0 };
        this.margin = { top: 32, bottom: 32, left: 32, right: 32 };
        this.ticks = { xMin: 0.0, xMax: 1.0, yMin: 0.0, yMax: 1.0, xStep: 0.2, yStep: 0.2 };
        this.options = options;
        this.plots = [];
        this.initCanvas();
    }
    initCanvas() {
        const dpr = window.devicePixelRatio || 1;
        if (!this.canvas.classList.contains("resized")) {
            this.canvas.width = this.width * dpr;
            this.canvas.height = this.height * dpr;
            this.canvas.style.width = this.width + 'px';
            this.canvas.style.height = this.height + 'px';
            this.ctx.scale(dpr, dpr);
            this.canvas.classList.add("resized");
        }
        this.width = this.canvas.width / dpr;
        this.height = this.canvas.height / dpr;
    }
    clear() {
        this.plots = [];
        this.draw();
    }
    plot(plot) {
        this.plots.push(plot);
    }
    draw() {
        this.updateMargin();
        this.updateView();
        this.updateTicks();
        this.ctx.clearRect(0, 0, this.width, this.height);
        if (this.options.grid)
            this.drawGrid();
        this.drawAxes();
        this.drawTicks();
        this.drawLabels();
        for (const plot of this.plots) {
            if (plot instanceof Graph)
                this.drawGraph(plot);
            else if (plot instanceof Scatter) {
                this.drawScatter(plot);
            }
        }
    }
    drawLine(xys) {
        this.ctx.beginPath();
        this.ctx.moveTo(xys[0][0], xys[0][1]);
        for (let i = 1; i < xys.length; ++i)
            this.ctx.lineTo(xys[i][0], xys[i][1]);
        this.ctx.stroke();
    }
    drawCircle(xy, radius) {
        this.ctx.beginPath();
        this.ctx.arc(xy[0], xy[1], radius, 0.0, 2.0 * Math.PI);
        this.ctx.fill();
    }
    drawGrid() {
        this.ctx.strokeStyle = '#bbb';
        this.ctx.lineWidth = 1;
        for (let y = this.ticks.yMin; y <= this.ticks.yMax; y += this.ticks.yStep) {
            const from = this.xy2uv(this.ticks.xMin, y);
            const to = this.xy2uv(this.ticks.xMax, y);
            this.drawLine([from, to]);
        }
        for (let x = this.ticks.xMin; x <= this.ticks.xMax; x += this.ticks.xStep) {
            const from = this.xy2uv(x, this.ticks.yMin);
            const to = this.xy2uv(x, this.ticks.yMax);
            this.drawLine([from, to]);
        }
    }
    drawAxes() {
        this.ctx.strokeStyle = this.variable("--main-text-color");
        this.ctx.lineWidth = 1;
        const origin = this.xy2uv(this.view.left, this.view.bottom);
        const right = this.xy2uv(this.view.right, this.view.bottom);
        const top = this.xy2uv(this.view.left, this.view.top);
        this.drawLine([top, origin, right]);
    }
    drawTicks() {
        this.ctx.strokeStyle = this.variable("--main-text-color");
        ;
        this.ctx.fillStyle = this.variable("--main-text-color");
        ;
        this.ctx.font = `0.75rem ${this.variable("--main-font")}`;
        const ticksLength = 3.0;
        for (const [dx, dy] of [[1.0, 0.0], [-1.0, 0.0], [0.0, 1.0], [0.0, -1.0]]) {
            for (let x = dx * this.ticks.xStep, y = dy * this.ticks.yStep; x >= this.ticks.xMin && x <= this.ticks.xMax && y >= this.ticks.yMin && y <= this.ticks.yMax; x += dx * this.ticks.xStep, y += dy * this.ticks.yStep) {
                const [px, py] = this.xy2uv(x, y);
                this.drawLine([
                    [px - Math.abs(dy) * ticksLength, py - Math.abs(dx) * ticksLength],
                    [px + Math.abs(dy) * ticksLength, py + Math.abs(dx) * ticksLength]
                ]);
                if (dx == 0.0) {
                    this.ctx.textAlign = 'right';
                    this.ctx.textBaseline = 'middle';
                    this.ctx.fillText(this.formatNumber(y), px - 2.0 * ticksLength, py);
                }
                if (dy == 0.0) {
                    this.ctx.textAlign = 'center';
                    this.ctx.textBaseline = 'top';
                    this.ctx.fillText(this.formatNumber(x), px, py + 2.0 * ticksLength);
                }
            }
        }
    }
    drawLabels() {
        const font = this.variable("--main-font");
        this.ctx.font = `0.75rem ${font}`;
        if (this.options.xlabel) {
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'middle';
            this.ctx.fillText(this.options.xlabel, this.width / 2.0, this.height - this.margin.bottom + 32);
        }
        if (this.options.ylabel) {
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'middle';
            this.ctx.rotate(-Math.PI / 2.0);
            this.ctx.fillText(this.options.ylabel, -this.height / 2.0, this.margin.left - 40);
            this.ctx.rotate(Math.PI / 2.0);
        }
        if (this.options.title) {
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'middle';
            this.ctx.font = `1rem ${font}`;
            this.ctx.fillText(this.options.title, this.width / 2.0, this.margin.top / 2.0);
        }
    }
    drawGraph(graph) {
        this.ctx.strokeStyle = this.variable("--primary-color");
        if (graph.options.color)
            this.ctx.strokeStyle = this.parseColor(graph.options.color);
        this.ctx.lineWidth = 2;
        this.drawLine(graph.pts.map((xy) => this.xy2uv(xy[0], xy[1])));
    }
    drawScatter(scatter) {
        this.ctx.fillStyle = this.variable("--primary-color");
        if (scatter.options.color)
            this.ctx.fillStyle = this.parseColor(scatter.options.color);
        this.ctx.lineWidth = 2;
        for (const xy of scatter.pts) {
            const uv = this.xy2uv(...xy);
            this.drawCircle(uv, 3);
        }
    }
    updateMargin() {
        this.margin = {
            top: (this.options.title ? 48 : 32),
            bottom: (this.options.xlabel ? 48 : 32),
            left: (this.options.ylabel ? 64 : 32),
            right: 32,
        };
    }
    updateView() {
        if (this.plots.length == 0) {
            this.view = { top: 1.0, bottom: 0.0, left: 0.0, right: 1.0 };
            return;
        }
        const view = { top: 1.0, bottom: 0.0, left: 0.0, right: 1.0 };
        for (const plot of this.plots) {
            for (const [x, y] of plot.pts) {
                view.left = Math.min(view.left, x);
                view.right = Math.max(view.right, x);
                view.top = Math.max(view.top, y);
                view.bottom = Math.min(view.bottom, y);
            }
        }
        this.view = view;
    }
    updateTicks() {
        this.ticks.xStep = 1.0;
        this.ticks.yStep = 0.1;
        this.ticks.xMin = Math.ceil(this.view.left / this.ticks.xStep) * this.ticks.xStep;
        this.ticks.yMin = Math.ceil(this.view.bottom / this.ticks.yStep) * this.ticks.yStep;
        this.ticks.xMax = Math.floor(this.view.right / this.ticks.xStep) * this.ticks.xStep;
        this.ticks.yMax = Math.floor(this.view.top / this.ticks.yStep) * this.ticks.yStep;
    }
    xy2uv(x, y) {
        return [
            this.margin.left + (x - this.view.left) / (this.view.right - this.view.left) * (this.width - this.margin.left - this.margin.right),
            this.height - this.margin.bottom - (y - this.view.bottom) / (this.view.top - this.view.bottom) * (this.height - this.margin.top - this.margin.bottom),
        ];
    }
    ;
    variable(name) {
        return getComputedStyle(this.canvas).getPropertyValue(name);
    }
    formatNumber(x) {
        const epsilon = 0.001;
        if (Math.abs(Math.round(x) - x) < epsilon)
            return x.toFixed();
        if (Math.abs(Math.round(10 * x) - 10 * x) < epsilon)
            return x.toFixed(1);
        if (Math.abs(Math.round(100 * x) - 100 * x) < epsilon)
            return x.toFixed(2);
        return x.toFixed(3);
    }
    parseColor(color) {
        if (color.startsWith("--"))
            return this.variable(color);
        else
            return color;
    }
}
