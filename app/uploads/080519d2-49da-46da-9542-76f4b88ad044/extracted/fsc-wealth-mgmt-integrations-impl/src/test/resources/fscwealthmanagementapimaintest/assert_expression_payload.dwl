%dw 2.0
import * from dw::test::Asserts
---
payload must equalTo({
  "Beneficiaries": {
    "Primary": [
      {
        "SharePercentage": "40",
        "SSN": "569-94-7726",
        "MobileNumber": "9876541234",
        "RelationshipType": "Grandson",
        "EmailAddress": "gabriel.bosso@gmail.com",
        "BeneficiaryType": "Individual",
        "Address": {
          "Country": "USA",
          "AddressLine2": "Floor 61",
          "AddressType": "Mailing Address",
          "State": "CA",
          "AddressLine1": "415 Mission St",
          "PostalCode": "94105",
          "City": "San Francisco"
        },
        "BeneficiaryDob": "04/06/1990",
        "PerStirpes": "yes",
        "BeneficiaryName": "Gabriel Basso",
        "BeneficiaryId": "BFR-0733674"
      },
      {
        "SharePercentage": "60",
        "SSN": "368-46-5302",
        "MobileNumber": "9807671486",
        "RelationshipType": "Mother",
        "EmailAddress": "canute.gomes@gmail.com",
        "BeneficiaryType": "Individual",
        "Address": {
          "Country": "USA",
          "AddressLine2": "Floor 61",
          "AddressType": "Mailing Address",
          "State": "CA",
          "AddressLine1": "415 Mission St",
          "PostalCode": "94105",
          "City": "San Francisco"
        },
        "BeneficiaryDob": "04/06/1990",
        "PerStirpes": "yes",
        "BeneficiaryName": "Canute Gomes",
        "BeneficiaryId": "BFR-1432051"
      }
    ],
    "Contingent": [
      {
        "SharePercentage": "40",
        "SSN": "569-94-7728",
        "MobileNumber": "9876541234",
        "RelationshipType": "Grandson",
        "EmailAddress": "ngela.bundalovic@gmail.com",
        "BeneficiaryType": "Individual",
        "Address": {
          "Country": "USA",
          "AddressLine2": "Floor 61",
          "AddressType": "Mailing Address",
          "State": "CA",
          "AddressLine1": "415 Mission St",
          "PostalCode": "94105",
          "City": "San Francisco"
        },
        "BeneficiaryDob": "04/06/1990",
        "PerStirpes": "yes",
        "BeneficiaryName": "Angela Bundalovic",
        "BeneficiaryId": "BFR-7773001"
      },
      {
        "SharePercentage": "60",
        "SSN": "617-10-7229",
        "MobileNumber": "9862433885",
        "RelationshipType": "Daughter",
        "EmailAddress": "shailyn.pierre@gmail.com",
        "BeneficiaryType": "Individual",
        "Address": {
          "Country": "USA",
          "AddressLine2": "Floor 61",
          "AddressType": "Mailing Address",
          "State": "CA",
          "AddressLine1": "415 Mission St",
          "PostalCode": "94105",
          "City": "San Francisco"
        },
        "BeneficiaryDob": "04/06/1990",
        "PerStirpes": "yes",
        "BeneficiaryName": "Shailyn Pierre",
        "BeneficiaryId": "BFR-6004202"
      }
    ]
  }
})