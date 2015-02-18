public enum MailScriptingClass: String {
    case RichText = "rich text"
    case Attachment = "attachment"
    case Paragraph = "paragraph"
    case Word = "word"
    case Character = "character"
    case AttributeRun = "attribute run"
    case OutgoingMessage = "outgoing message"
    case LdapServer = "ldap server"
    case OldMessageEditor = "OLD message editor"
    case MessageViewer = "message viewer"
    case Signature = "signature"
    case Message = "message"
    case Account = "account"
    case ImapAccount = "imap account"
    case IcloudAccount = "iCloud account"
    case PopAccount = "pop account"
    case SmtpServer = "smtp server"
    case Mailbox = "mailbox"
    case Rule = "rule"
    case RuleCondition = "rule condition"
    case Recipient = "recipient"
    case BccRecipient = "bcc recipient"
    case CcRecipient = "cc recipient"
    case ToRecipient = "to recipient"
    case Container = "container"
    case Header = "header"
    case MailAttachment = "mail attachment"
}