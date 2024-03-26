var data = [
    {
        "name": "model_name",
        "label": "The name of the model as seen on the model page"
    },
    {
        "name": "model_version",
        "label": "The version of the model"
    },
    {
        "name": "model_creator",
        "label": "The creator of the model"
    },
    {
        "name": "model_base",
        "label": "The base model of the model (1.5, SDXL, Pony, etc.)"
    },
    {
        "name": "model_type",
        "label": "The type of the model (Lora, Checkpoint, Embedding, etc.)"
    },
];

function settingsHints() {
    var table = document.createElement('table');
    table.className = 'popup-table';

    data.forEach(function(obj) {
        var tr = document.createElement('tr');
        var td = document.createElement('td');
        td.textContent = obj.name;
        tr.appendChild(td);

        td = document.createElement('td');
        td.textContent = obj.label;
        tr.appendChild(td);

        table.appendChild(tr);
    });

    popup(table);
}