// GameStorm Scripts

// Connect to TON Keeper
async function connectToTON() {
    if (window.ton) {
        try {
            await window.ton.connect();
            console.log("Connected to TON Keeper");
            return true;
        } catch (e) {
            console.error("TON Connection Error:", e);
            return false;
        }
    }
    return false;
}

// Start Game
function startGame(gameType) {
    if (gameType === "football") {
        window.location.href = "games/football.html";
    } else if (gameType === "puzzle") {
        window.location.href = "games/puzzle.html";
    } else if (gameType === "duel") {
        window.location.href = "games/duel.html";
    }
}

// Buy NFT
async function buyNFT(itemId) {
    const nfts = await fetch("nfts.json").then(res => res.json());
    const nft = nfts.find(n => n.id === itemId);
    if (nft && await connectToTON()) {
        try {
            await window.ton.sendTransaction({
                to: "UQBbDbfN09WPh5vbQwuQNwAYi_GLhSo2MXF1-MK8m002Pixc",
                value: nft.price,
                data: `Buy ${nft.name}`
            });
            alert(`Purchased ${nft.name} for ${nft.price} TON!`);
        } catch (e) {
            alert("Transaction circ: Failed to buy NFT: " + e.message);
        }
    }
}

// Load NFTs
fetch("nfts.json")
    .then(res => res.json())
    .then(nfts => {
        const nftContainer = document.getElementById("nfts");
        nfts.forEach(nft => {
            const card = document.createElement("div");
            card.className = "nft-card";
            card.innerHTML = `
                <img src="${nft.image}" alt="${nft.name}">
                <p>${nft.name} - ${nft.price} TON</p>
            `;
            card.onclick = () => buyNFT(nft.id);
            nftContainer.appendChild(card);
        });
    });

// Load Leaderboard
fetch("/leaderboard")
    .then(res => res.json())
    .then(data => {
        const list = document.getElementById("leaderboard-list");
        data.forEach((entry, index) => {
            const li = document.createElement("li");
            li.textContent = `${index + 1}. ${entry.user} - ${entry.points} Points`;
            list.appendChild(li);
        });
    });
