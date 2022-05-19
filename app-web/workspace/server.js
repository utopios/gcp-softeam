const express = require("express")

const app = express()

app.get("/", (req, res) => {
    res.end("Bonjour tout le monde")
})

app.listen(80, () => {

})