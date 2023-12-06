const { Rettiwt } = require("rettiwt-api")
const fs = require("fs")
const ini = require("ini")
const path = require("path")
const util = require("util")
const sleep = util.promisify(setTimeout)
require("dotenv").config()

// Login to rettiwt with API Key generated using rettiwt-auth
const rettiwt = new Rettiwt({
    apiKey: process.env.SESSION_API_KEY,
})

// Parse the config file
const config = ini.parse(fs.readFileSync(path.join(__dirname, "config.ini"), "utf-8"))
const searchModes = ["Hashtags", "Words", "UserSets"]
const minViewCount = config["SearchControls"]["MinViewCount"]

// Function to choose a random property from a section
function chooseRandomProperty(obj) {
    const keys = Object.keys(obj)
    return obj[keys[Math.floor(Math.random() * keys.length)]]
}

// Function to handle the search and file writing
async function handleSearchAndWrite(searchMode, searchValue) {
    try {
        const data = await rettiwt.tweet.search({
            [searchMode.toLowerCase()]: searchValue,
            replies: false,
        })
        console.log(data)

        const filteredTweets = data.list
            .filter((tweet) => tweet.lang === "en")
            .map((tweet) => ({
                id: tweet.id.toString(),
                text: tweet.fullText,
            }))

        if (filteredTweets.length > 0) {
            const batchName = `../posting/selected_tweets/batch_${data.next.value}.json`
            await fs.promises.writeFile(batchName, JSON.stringify(filteredTweets, null, 2))
            console.log(`Wrote ${filteredTweets.length} tweet(s) to ${batchName}`)
            return { actions: 1, tweets: filteredTweets.length }
        } else {
            console.log("No tweets matched the criteria.")
            return { actions: 0, tweets: 0 }
        }
    } catch (err) {
        console.log("Error during search and write:", err)
        return { actions: 0, tweets: 0 }
    }
}

async function main() {
    let totalActions = 0
    let totalTweets = 0

    while (true) {
        // Choose a search mode at random
        let searchMode = searchModes[Math.floor(Math.random() * searchModes.length)]

        // Choose a random value for corresponding searchMode from config.ini
        let searchValue = chooseRandomProperty(config[searchMode])

        if (searchMode === "UserSets") {
            // If the searchMode is UserSets, split the string into an array
            searchValue = searchValue.split(", ").map((item) => item.trim())
        } else {
            // For Hashtags and Words, wrap the string in an array
            searchValue = [searchValue]
        }

        console.log(`New search mode = ${searchMode}`)
        console.log(`New search value = ${searchValue}`)

        const result = await handleSearchAndWrite(searchMode, searchValue)
        totalActions += result.actions
        totalTweets += result.tweets

        console.log(`Total actions performed this session: ${totalActions}`)
        console.log(`Total tweets selected this session: ${totalTweets}`)

        console.log(`Resting 45- 60 mins`)
        await sleep(Math.floor(Math.random() * (3600000 - 2700000 + 1)) + 2700000)
    }
}

main()
