function Test()
{
	alert("Hello World!");
}

var btn = document.getElementById('testButton');
btn.addEventListener('click', Test, true);