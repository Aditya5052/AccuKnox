SELECT STRING_AGG([Mobile__c], ',') as Mobile__c
FROM [sfdc].[case]
LEFT JOIN [sfdc].[Asset]
ON [AssetId] = [Asset].[Id]
LEFT JOIN [sfdc].[Product2]
ON [Product2Id] = [Product2].[Id]
WHERE [case].RecordTypeId = '0122v000001by3JAAQ'
AND [Asset].[Is_GMC_Policy__c] = 1 
AND [case].[Mobile__c] NOT IN ('5555555555','9999999999','8888888888')
AND [case].[Mobile__c] NOT LIKE ('1%') AND [case].[Mobile__c] NOT LIKE ('2%') AND [case].[Mobile__c] NOT LIKE ('4%')
AND [case].[Mobile__c] NOT LIKE ('5%')
AND [case].[Invoice_Number__c] IS NOT NULL AND [case].[Invoice_Number__c] NOT IN ('123', '1234')
AND [OpenLoop_Hospital_Name__c] IS NOT NULL
AND CAST([Approved_Amount__c] AS FLOAT)>999
AND ([Mobile__c] IN {productMobiles} OR [HAN_From_Policy__c] IN {productHANs})
GROUP BY UPPER([OpenLoop_Hospital_Name__c]),
(CASE WHEN [Approved_Amount__c] IS NOT NULL THEN [Approved_Amount__c]
ELSE [Bill_Amount__c] END)
HAVING MAX([case].[CreatedDate])>MIN([BH_Reimbursement_Paid_Time__c])
AND (STRING_AGG([case].[Status], ',') LIKE '%New%' OR STRING_AGG([case].[Status], ',') LIKE '%Paid,Paid%')
ORDER BY SUM(CAST([Approved_Amount__c] as FLOAT)) DESC