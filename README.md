# Analysis of Olympic Performance for Countries based on Government Type and Change in Government Throughout the Years

**Team**: Snehal Lokesh (slokesh2); Sushma Mahadevaswamy (sushmam3); Sushanth Sreenivasa Babu (ss142)

<p align="center">
     <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Olympic_rings_without_rims.svg/2880px-Olympic_rings_without_rims.svg.png" width="500" height="300">
     <img src="https://assets.telegraphindia.com/telegraph/bb5aaa2f-4a8a-4ae9-81c3-24816f1ea88c.jpg" width="500" height="250">
</p>

The Olympics is a global sporting event with more than 200 participants. These games are held every 4 years where countries showcase their athletic might. 

The 20th Century saw the many countries change their government type and we also witnessed divisions and emergence of newer countries. With these instances in mind, we try to see if there has been a change in the Olympic performance of countries that had a change in their government type.  

We analyze countries with short-term changes in the government type before reverting back to the original type, analyze the data during this time and see if this had an effect on the future events, and also see if there are long term effects on performance and representation, essentially to see if there is a lag in this because of the short-term change in the government type.

## Datasets Used:

- 120 Years Olympics Data: https://www.kaggle.com/heesoo37/120-years-of-olympic-history-athletes-and-results
     
     The data has the following columns   
     - ID - Unique number for each athlete
     - Name - Athlete's name
     - Sex - M/F
     - Age - Integer
     - Height - In centimeters
     - Weight - In kilograms
     - Team - Team name
     - NOC - National Olympic Committee 3-letter code
     - Games - Year and season
     - Year - Integer
     - Season - Summer or Winter
     - City - Host city
     - Sport - Sport
     - Event - Event
     - Medal - Gold, Silver, Bronze, or NA  


- World Systemic Peace Dataset: https://www.systemicpeace.org/polityproject.html
     
     We use the following columns:   
     - Year: Integer
     - Country: Unique countries
     - polity2: -10 to +10 (completely autocratic to completely democratic)
     - scode: Country Identifier
     
     
- IMF GDP Data: https://www.imf.org/en/Publications/WEO/weo-database/2021/October/download-entire-database
     
     We use the following columns:   
     - Year: Integer
     - Country: Unique countries
     - GDP in Billion USD

## Olympic Success 
We would look at a country's success in the Olympics based on the following metrics:

*Some metrics are normalized to incorporate the number of participants in each country and year*

- Number of Participants
- Medals Won (Gold, Silver, Bronze)
- Medals Won as % of Total Participants
- Medals to Participants Ratio
- Male to Female Representation
- Average Age


Note: The olympics were cancelled during World War I (1916) and World War II (1940 and 1944)

## Code Procedure

With the help of our custom built **"helper_function.py" module** which houses 20 functions to take care of every part of our cleaning and exploration, we were able to plot graphs for different countries, metrics and year ranges. 

We have used python libraries like **pandas, numpy, plotly and ipywidgets** to achieve our overall goal of analyzing the olympic performace indicators and coming up with a conclusion. 

In order to improve our code performance efficiency, we have employed **parallel processing** to plot graphs for the different metrics. 

We have also included doctests and detailed docstrings for code reproducibility. Finally, we have incorporated **GitHub actions for CI/CD** to maintain code quality and integrity.

## Results of Analysis
### KOREA:

In 1945, Korea split into North Korea (Autocratic) and South Korea (Democratic). During 1960, the April Revolution caused president Syngman Rhee to resign which is why the polity score might have dipped. Since 1972, South Korea's polity score increased, as it became more and more democratic. This might be a cause for its increase in performance over the next few years. While North Korea continued to grow as an autocracy, its performance in Olympics decreased. 1960 onwards, South Korea moved from a low income to middle income country which might have caused an increase in the participation ratio when compared to North Korea. The Male participation was found to be more in South Korea while female participation vs male participation was higher in North Korea.

Reference: 

1. https://www.pbs.org/wnet/wideangle/uncategorized/north-korea-and-the-korean-war-1945-1949-background/1347/#:~:text=In%201945%2C%20Korea%20was%20faced,American%20forces%20in%20the%20south.&text=At%20war's%20end%2C%20among%20the,Sung%2C%20a%20Soviet%20army%20captain.
2. https://en.wikipedia.org/wiki/Division_of_Korea

<p align="center">
<img src="https://i.pinimg.com/736x/1d/a1/79/1da17947aa09c9389b9ac7aecc082ae0.jpg" width="150" height="250">
</p>

![newplot](https://user-images.githubusercontent.com/41410488/145706043-3ca73c2c-002c-4fa1-8f51-267bb41c9b29.png)
![newplot (1)](https://user-images.githubusercontent.com/41410488/145706047-a38f0ee4-35dc-4973-9ea2-286493795360.png)
![newplot (2)](https://user-images.githubusercontent.com/41410488/145706051-63358a47-ef82-4a11-a17d-0fa96323aa98.png)
![newplot (3)](https://user-images.githubusercontent.com/41410488/145706055-9c63f222-b168-45f8-8396-f2bd805c461c.png)
![newplot (4)](https://user-images.githubusercontent.com/41410488/145706056-a82bd827-6631-4d5c-8133-c3edb5f3af70.png)
![newplot (10)](https://user-images.githubusercontent.com/41410488/145706510-d1a1728a-1d53-4159-b219-fcf0dcc6e3be.png)


### GDP and Polity Score vs Olympic Performance

We thought maybe we could incorporate GDP as well to see if both have an effect on the overall results in olympics. The dynamic function "plot_graphs_for_country" automatically adds a GDP subplot based on the parameters passed.

_Note: Some countries do not have GDP value in the IMF dataset. This is the reason why countries like Afghanistan don't have a visible curve in the graph_

**China** has had -7 score since 1980 but its GDP has been increasing ever since, we also notice an increase in medals to participant ratio and an overall increase in the metrics. Female participants ratio has been increasing with the 2012 and 2016 events noting higher female participation.

![newplot (5)](https://user-images.githubusercontent.com/41410488/145706112-f44ae59a-8a9b-4e4c-bf8b-223360c2a137.png)
![newplot (6)](https://user-images.githubusercontent.com/41410488/145706113-2d9400ae-e298-4bfc-aa79-f1b64915bfc1.png)
![newplot (7)](https://user-images.githubusercontent.com/41410488/145706117-e4015bec-5cbd-4b83-8553-213c99e48aea.png)
![newplot (8)](https://user-images.githubusercontent.com/41410488/145706120-274ed29f-03a5-407a-8330-fc4415dc1af2.png)
![newplot (9)](https://user-images.githubusercontent.com/41410488/145706133-0df18313-55ad-4aa4-af34-537c524fb393.png)
![newplot (11)](https://user-images.githubusercontent.com/41410488/145706555-77aa7691-38e5-4336-852e-b5688a8f06ef.png)


**Note**: Refer Notebook for interactive functionality

# CONCLUSION

Countries have indeed witnessed changes in Olympic metrics that we defined. The world wars have changed many countries and their political stance, this has caused an increase or decrease in Olympic metrics. In general, the developing countries that are newly democratic are witnessing slow but steady increase in Olympic performace. However, China, for example, has witnessed steep rise in Olympic Metrics while North Korea which also has a complete autocratic score has seen a decline in most of the metrics.

**Medals Won vs Polity Score** <br>
**Medals Won as % of Total Participants** <br>
**Medals to Participants Ratio:** <br>
Strong democracies have generally witnessed a consistently higher success in this metric. Growing democracies, however, are showing slow signs of improvement. Complete autocracies with high GDP generally have high success in this metric, with many gulf countries being a exception. On the other hand, autocracies with low GDP have poor success in this metric.


**Average Age**: <br>
Generally, the average age has reduced since the world wars, with younger population being represented on a larger scale with all the countries. Gulf autocracies like Saudi Arabia and Kuwait, for example, however have shown an increase in this metric even though their GDP is high.

**Number of Participants**: <br>
This metric has also been increasing generally. However, when countries are affected by war, this takes a hit and reduces. For instance, the gulf war has decreased participants in the subsequent years. 

**Male and Female Representation**: <br>
The female representation is generally increasing, this is more evident in democratic countries. Some autocracies like China have also increased their female representation with instances of having more female participants than their male counter parts. Gulf countries, however, have poor female representation but it is slowly increasing as well.


