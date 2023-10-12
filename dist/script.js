// 获取DOM元素
const editor = document.getElementById('editor');
const submitBtn = document.getElementById('submit');
const refreshBtn = document.getElementById('refresh');

// 初始化
let token = prompt('请输入token');

let headers = new Headers();
headers.append('Authorization', 'Bearer ' + token);

let requestOptions = {
    headers: headers
};

verifyToken(token)
    .then(res => {
        if (res) {
            initEditor();
        } else {
            alert('无效token');
        }
    });

// 初始化编辑器
function initEditor() {
    fetch('/getAllModelConfig', requestOptions)
        .then(res => res.text())
        .then(text => {
            const data = JSON.parse(text);
            const formatted = JSON.stringify(data, null, 2);

            editor.value = formatted;
        });
}

// 提交事件
submitBtn.addEventListener('click', () => {
    let text = editor.value;

    fetch('/updateModelConfig', {
        method: 'POST',
        body: text,
        headers: new Headers({
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token
        }),
    });
});

// 刷新事件
refreshBtn.addEventListener('click', () => {
    initEditor();
});

// Token验证
function verifyToken(token) {
    return fetch('/verify', requestOptions)
        .then(res => res.json())
        .then(data => {
            return data.success;
        });
}