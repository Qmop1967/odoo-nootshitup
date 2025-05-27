# Post-Publish Script Setup Guide

This guide explains how to set up and use post-publish scripts for the TSH Salesperson App.

## 📁 Available Scripts

### 1. `scripts/post_publish.sh` - Comprehensive Post-Publish Script
A full-featured script that handles:
- ✅ Deployment status logging
- 📢 Notifications (ready for Slack/Discord/Teams integration)
- 💾 Backup of release artifacts
- 📝 Version tracking and release notes generation
- 🧹 Cleanup of temporary files
- 📊 Build information logging

### 2. `scripts/codemagic_post_publish.sh` - Codemagic Optimized
A lightweight script optimized for Codemagic CI/CD:
- 📱 Logs build information
- 🧹 Basic cleanup tasks
- ✅ Success notifications
- 📊 Deployment status tracking

## 🚀 Setup Instructions

### For Codemagic

1. **Automatic Setup**: The script is already configured in `codemagic.yaml` under the production workflow.

2. **Manual Configuration**: If you need to add it to other workflows, add this to your publishing section:

```yaml
publishing:
  # ... other publishing configurations ...
  
  # Post-publish script
  scripts:
    - name: Post-publish Tasks
      script: |
        echo "🚀 Running post-publish script..."
        chmod +x scripts/codemagic_post_publish.sh
        ./scripts/codemagic_post_publish.sh
```

### For Other CI/CD Platforms

1. **GitHub Actions**: Add to your workflow after the publish step:
```yaml
- name: Run Post-Publish Script
  run: |
    chmod +x scripts/post_publish.sh
    ./scripts/post_publish.sh
```

2. **GitLab CI**: Add to your `.gitlab-ci.yml`:
```yaml
post_publish:
  stage: deploy
  script:
    - chmod +x scripts/post_publish.sh
    - ./scripts/post_publish.sh
  only:
    - main
```

3. **Local Development**: Run manually after publishing:
```bash
chmod +x scripts/post_publish.sh
./scripts/post_publish.sh
```

## 🔧 Customization

### Adding Notifications

To add Slack notifications, modify the `send_notification` function in `scripts/post_publish.sh`:

```bash
send_notification() {
    local message="$1"
    echo "📢 Notification: $message"
    
    # Slack webhook
    if [ -n "$SLACK_WEBHOOK_URL" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"$message\"}" \
            "$SLACK_WEBHOOK_URL"
    fi
    
    # Discord webhook
    if [ -n "$DISCORD_WEBHOOK_URL" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"content\":\"$message\"}" \
            "$DISCORD_WEBHOOK_URL"
    fi
}
```

### Environment Variables

Set these environment variables for enhanced functionality:

- `SLACK_WEBHOOK_URL`: Slack webhook for notifications
- `DISCORD_WEBHOOK_URL`: Discord webhook for notifications
- `BACKUP_ENABLED`: Set to "true" to enable artifact backups
- `CLEANUP_ENABLED`: Set to "true" to enable cleanup tasks

### Codemagic Environment Variables

The scripts automatically use these Codemagic variables:
- `CM_BUILD_VERSION`: App version
- `CM_BUILD_NUMBER`: Build number
- `CM_BRANCH`: Git branch
- `CM_BUILD_TYPE`: Build type (release/debug)
- `CM_COMMIT`: Git commit hash

## 📊 Generated Files

The post-publish scripts create several files for tracking:

- `deployment_log.json`: JSON log of deployments
- `release_history.log`: Text log of releases
- `latest_changes.md`: Changelog since last tag
- `.post_publish_success`: Success marker file
- `release_backups/`: Directory with artifact backups

## 🔍 Monitoring

### Check Script Execution
```bash
# Check if post-publish ran successfully
ls -la .post_publish_success

# View deployment log
cat deployment_log.json

# View release history
cat release_history.log
```

### Debug Issues
```bash
# Run script manually with debug output
bash -x scripts/post_publish.sh

# Check script permissions
ls -la scripts/post_publish.sh
```

## 🛠️ Troubleshooting

### Common Issues

1. **Permission Denied**
   ```bash
   chmod +x scripts/post_publish.sh
   chmod +x scripts/codemagic_post_publish.sh
   ```

2. **Script Not Found**
   - Ensure scripts are in the `scripts/` directory
   - Check file paths in your CI/CD configuration

3. **Environment Variables Missing**
   - Verify CI/CD platform provides expected variables
   - Add fallback values in scripts if needed

### Logs and Debugging

- All scripts use `set -x` for detailed execution logs
- Check CI/CD platform logs for script output
- Use `echo` statements to track script progress

## 🔄 Integration with Workflows

The post-publish scripts integrate with:

- ✅ **Codemagic**: Configured in `codemagic.yaml`
- ✅ **GitHub Actions**: Ready for integration
- ✅ **GitLab CI**: Ready for integration
- ✅ **Local Development**: Can be run manually

## 📈 Future Enhancements

Planned improvements:
- 📧 Email notifications
- 📊 Analytics integration
- 🔄 Automated rollback capabilities
- 📱 Mobile app notifications
- 🔍 Advanced error reporting

## 🤝 Contributing

To improve the post-publish scripts:
1. Edit the scripts in the `scripts/` directory
2. Test locally before committing
3. Update this documentation if adding new features
4. Ensure backward compatibility

---

For questions or issues, contact the development team or create an issue in the repository.