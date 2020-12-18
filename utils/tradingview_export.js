// Copyright: https://github.com/QuantNomad/research/blob/master/tv_stuff/js_code_to_copy_tv_trades.txt
// Write this into the console in Tradingview Strategy tester

// declaring functions
function exists(keys) {
    let key, parent = window;
    for (let i = 0; i < keys.length; i++) {
        key = keys[i];
        if (!parent.hasOwnProperty(key)) {
            return;
        }

        parent = parent[key];
    }

    return parent;
}

function type(k) {
    const a = {"le": "Entry Long", "lx": "Exit Long", "se": "Entry Short", "sx": "Exit Short"};

    return a.hasOwnProperty(k) ? a[k] : undefined;
}

function tz(n) {
    return n.replace(/([0-9]+(\.[0-9]+[1-9])?)(\.?0+$)/, "$1")
}

function mv(a, k) {
    if (typeof k === "function") {
        return a.push(k());
    }

    if (typeof k === "string") {
        const reg = /^(\$)?(.+?)(?:\.(\d+))?(%)?$/;
        const res = reg.exec(k);

        if (!a.hasOwnProperty(res[2])) {
            return;
        }

        res[1] = /*res[1] ||*/ "";
        res[2] = a[res[2]];
        res[3] = +res[3] || 0;
        res[4] = /*res[4] ||*/ "";

        if (res[2] === null) {
            return "N/A";
        }
        if (res[4] === "%") {
            res[2] *= 100;
        }
        if (k === "profitFactor" && res[2] < 1) {
            res[2] *= -1;
        }

        return res[1] + tz(res[2].toFixed(res[3])) + res[4];
    }

    throw new TypeError("Unsupported type: " + typeof k);
}

function dt(timestamp) {
    const D = new Date(timestamp);
    const d = [D.getFullYear(), p(D.getMonth() + 1), p(D.getDate())].join("-");
    const t = [p(D.getHours()), p(D.getMinutes()), p(D.getSeconds())].join(":");

    return d + " " + t;
}

function p(x) {
    return (x.length === 1 || x < 10) ? "0" + x : x;
}

function output(trades) {
    let ret = [];

    trades.items = trades.items.map(tab);
    ret.push(trades.headings.join("\t"));
    ret = ret.concat(trades.items);

    return ret.join("\n");
}

function tab(array) {
    return array.join("\t");
}

function clipboard(format, data) {
    const tmp = document.oncopy;

    document.oncopy = function clipboard_oncopy(e) {
        e.clipboardData.setData(format, data);
        e.preventDefault();
    };
    document.execCommand("copy", false, null);
    alert("Copied to Clipboard");

    document.oncopy = tmp;
}

// defining variables
var rw_new = exists("TradingView.bottomWidgetBar._widgets.backtesting._reportWidgetsSet.reportWidget".split("."))
var data_new = rw_new._data;
var t_new = data_new.trades;
var sd_new = rw_new._report._seriesDecimals || 2

// parsing trades
let trades3 = {
    headings: "Trade #,Type,Signal,Date/Time,Price,Contracts,Profit,ProfitPerc,ProfitEqPerc,ProfitEq,RunUpPerc,RunUp,DrawdownPerc,Drawdown".split(","),
    items: []
};
for (i = 0; i < t_new.length; i++) {
    v = t_new[i];
    trades3.items.push([i + 1, type(v.e.tp), v.e.c, dt(v.e.tm), mv(v.e, "$p." + sd_new), ,]);
    trades3.items.push(v.x.c.length
        ? [, type(v.x.tp), v.x.c, dt(v.x.tm), mv(v.x, "$p." + sd_new), v.q, tz(v.pf.toFixed(sd_new)), tz(v.tp.p.toFixed(sd_new)), tz(v.cp.p.toFixed(sd_new)), tz(v.cp.v.toFixed(sd_new)), tz(v.rn.p.toFixed(sd_new)), tz(v.rn.v.toFixed(sd_new)), tz(v.dd.p.toFixed(sd_new)), tz(v.dd.v.toFixed(sd_new))]
        : [, type(v.x.tp), "Open", , , , ,]
    );
}

// Copying trades to the clipboard
clipboard("text/plain", output(trades3))