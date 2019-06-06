const request = require('request');
const cheerio = require('cheerio');
const fs = require('fs');
const stringify = require('csv-stringify');

const moviesURL = "https://www.mxplayer.in/movies";
const seriesURL = "https://www.mxplayer.in/web-series";
const showsURL = "https://www.mxplayer.in/shows";

crawlWebsite('movies', moviesURL, './Data/movieData.csv');
crawlWebsite('webSeries', seriesURL, './Data/seriesData.csv');
crawlWebsite('TVShows', showsURL, './Data/showsData.csv');

function crawlWebsite(section, url, filename){
    request(url, function(err, res, body){
        finalResult = [];
        if(err){
            console.log('error occured : ', err);
        }
        else{
            let $ = cheerio.load(body);
            $('div.section > div.section-content-container > div.card-slider > div.slider-container > div.slides-wrapper > div.slides-container \
                > div.slide')
            .each(function(){
                let data = $(this);
                let title = data.find('div.card-header').text();
                let description = data.find('div.card-subheader').text().split(', ');
                obj = DataToObject(section, title, description);
                finalResult.push(obj);
            })
        }
        writeIntoFile(finalResult, filename);
    });
    
}

function DataToObject(section, title, description){
    var obj;
    if(section == 'movies'){
        obj = moviesDataToObject(title, description);
    } else{
        obj = regularDataToObject(title, description);
    }
    return obj;
}

function writeIntoFile(data, filename){
    console.log(data);
    
    fields = ['title','type', 'numberOfSeasons', 'numberOfEpisodes', 'language', 'yearOfRelease'];
    stringify(data, { header: true, columns: fields }, (err, output) => {
        if (err){
            throw err;
        }
        fs.writeFile(filename, output, (err) => {
          if (err) throw err;
          console.log(filename, 'saved.');
        });
      });
};

function moviesDataToObject(title, desc){
    let type = desc[0];
    let lang = desc[1];
    let yearOfRelease = desc[2];
    let obj = {
        title : title,
        type : type,
        numberOfSeasons : '',
        numberOfEpisodes : '',
        language : lang,
        yearOfRelease : yearOfRelease
    }
    return obj;
};

function regularDataToObject(title, desc){
    let numberOfSeasons = desc[0];
    let numberOfEpisodes = desc[1];
    // let yearOfRelease = desc[2];
    let obj = {
        title : title,
        type : '',
        numberOfSeasons : numberOfSeasons,
        numberOfEpisodes : numberOfEpisodes,
        language : '',
        yearOfRelease : ''
    }
    return obj;
};
