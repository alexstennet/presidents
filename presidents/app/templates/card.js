class Card {
    constructor(value) {
        this.value = value;
        this.clicked = false;
        console.log('created');
    }

    createBtn() {
        var btn = document.createElement('input');
        btn.type = 'button';
        return btn;
    }
}