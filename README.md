# Analysis of Olympic Performance of Countries based on Government Type and Change in Government Throughout the Years

<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Olympic_rings_without_rims.svg/2880px-Olympic_rings_without_rims.svg.png" width="450" height="300">

<img src="https://assets.telegraphindia.com/telegraph/bb5aaa2f-4a8a-4ae9-81c3-24816f1ea88c.jpg" width="450" height="250">

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


- World Governance Indicators: https://info.worldbank.org/governance/wgi/

    We plan to use the following columns:
    - Year - Integer
    - Country - Unqi
    - polity2 - -10 to +10 (completely autocratic to completely democratic)
    - scode - country identifier

## Final Analysis
We would measure a country's success in the Olympics based on the following metrics:
- Number of Participants
- Medals won (Gold, Silver, Bronze)
- Medals to Participants Ratio
- Male to Female Representation
- Average Age

### Results of Analysis

#### KOREA:

In 1945, Korea split into North Korea (Autocratic) and South Korea (Democratic). During 1960, the April Revolution caused president Syngman Rhee to resign which is why the polity score might have dipped. Since 1972, South Korea's polity score increased, as it became more and more democratic. This might be a cause for its increase in performance over the next few years. While North Korea continued to grow as an autocracy, its performance in Olympics decreased. 1960 onwards, South Korea moved from a low income to middle income country which might have caused an increase in the participation ratio when compared to North Korea. The Male participation was found to be more in South Korea while female participation vs male participation was higher in North Korea.

![newplot](https://user-images.githubusercontent.com/41410488/144549036-59e3afce-eee4-40ca-a462-711b226d9a7a.png)
![newplot (1)](https://user-images.githubusercontent.com/41410488/144549179-121b3d78-2498-4a00-bb5d-503c124cd345.png)
![newplot (2)](https://user-images.githubusercontent.com/41410488/144549186-3aba2b54-db90-4374-8382-41c62b49b129.png)
![newplot (3)](https://user-images.githubusercontent.com/41410488/144549214-8d323d72-9eb2-4bcf-b810-fc641320fc72.png)
![newplot (4)](https://user-images.githubusercontent.com/41410488/144549240-32e6783c-5776-4aeb-884f-c456c17909b3.png)


