# LandlordList API

Python JSON API for the website landlordlist.uk

## Endpoints
All endpoints are GET

### /api/parties
Returns a JSON array containing a list of political parties present in the UK House of Commons or the House of Lords.

### /api/parties/{id}
Returns a JSON object containing details of a single party.

### /api/people
Returns a list of members of either House.

Limited to 10 results.

#### Query parameters
| Parameters      | Description                                                                                 |
|-----------------|---------------------------------------------------------------------------------------------|
| ```offset```    | Set the SQL offset parameter                                                                |
| ```house```     | Can be either 'Commons' or 'Lords'. Filters members shown to members of the specified house |
| ```landlords``` | Set to 1 to return landlords only. Omit for all members.                                    |

### /api/people/{id}
Return JSON object with details of a single person.

### /api/houses
Returns array of houses (i.e. Commons and Lords)

### /api/houses/{id}
Returns an object containing statistics.

It shows:
* Number of members in the house
* Number of landlordds
* A list of the parties and how many members and landlords in each