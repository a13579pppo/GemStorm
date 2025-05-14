// Football Game with Phaser.js
const config = {
    type: Phaser.AUTO,
    width: window.innerWidth,
    height: window.innerHeight,
    scene: {
        preload: preload,
        create: create,
        update: update
    },
    physics: {
        default: 'arcade',
        arcade: {
            gravity: { y: 0 }
        }
    }
};

const game = new Phaser.Game(config);

function preload() {
    this.load.image('ball', '../assets/football.png');
    this.load.image('player', '../assets/player.png');
}

function create() {
    // Create football field
    this.add.rectangle(0, 0, window.innerWidth, window.innerHeight, 0x00ff00).setOrigin(0);
    
    // Create ball
    const ball = this.physics.add.image(window.innerWidth / 2, window.innerHeight / 2, 'ball')
        .setCollideWorldBounds(true)
        .setBounce(1);
    
    // Create player
    const player = this.physics.add.image(100, 100, 'player')
        .setCollideWorldBounds(true);
    
    this.physics.add.collider(ball, player);
    
    // Controls
    this.cursors = this.input.keyboard.createCursorKeys();
}

function update() {
    const player = this.physics.world.bodies.entries[1];
    if (this.cursors.left.isDown) {
        player.setVelocityX(-200);
    } else if (this.cursors.right.isDown) {
        player.setVelocityX(200);
    } else {
        player.setVelocityX(0);
    }
    
    if (this.cursors.up.isDown) {
        player.setVelocityY(-200);
    } else if (this.cursors.down.isDown) {
        player.setVelocityY(200);
    } else {
        player.setVelocityY(0);
    }
}
