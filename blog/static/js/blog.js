document.addEventListener('DOMContentLoaded', () => {

    document.getElementById('myBtn').addEventListener('click', () => {
        document.querySelector('.bg-modal').style.display = 'flex';
    });

    document.querySelector('.close').addEventListener('click', () => {
        document.querySelector('.bg-modal').style.display = 'none';
    });
});