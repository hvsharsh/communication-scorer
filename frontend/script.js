async function scoreNow(){
let text=document.getElementById("textInput").value;
let res=await fetch("http://localhost:8000/score",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({transcript:text})});
let data=await res.json();
let out="<h2>Overall Score: "+data.overall_score+"</h2>";
out+="<p>Word Count: "+data.word_count+"</p>";
data.criteria.forEach(c=>{
out+=`<h3>${c.criterion}</h3>
<p>Score: ${c.score}</p>
<p>Keywords Found: ${c.keywords_found}</p>
<p>Similarity: ${c.similarity}</p>
<p>${c.feedback}</p><hr>`;
});
document.getElementById("output").innerHTML=out;
}
