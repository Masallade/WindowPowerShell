// This function collects all open tab info and sends it to a local server
async function reportTabs() {
    let tabs = await chrome.tabs.query({});
    let tabData = tabs.map(tab => ({
        title: tab.title,
        url: tab.url
    }));

    // Send to local Python server
    fetch("http://127.0.0.1:5000/report_tabs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(tabData)
    }).catch(err => {
        // Ignore errors if server is not running
    });
}

// Report tabs every 30 seconds
setInterval(reportTabs, 30000);
// Also report immediately on extension load
reportTabs();